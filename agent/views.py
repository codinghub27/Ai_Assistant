from django.shortcuts import render, redirect
from django_ratelimit.core import is_ratelimited
from rest_framework.views import APIView
from rest_framework.response import Response
from .agent import get_agent
from .models import ResearchSession,Query
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import json
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .serializers import ResearchSerializer
from drf_spectacular.utils import extend_schema
from django.contrib.auth.decorators import login_required
import re


def extract_sources(intermediate_steps, max_sources=6):
    """Collect unique, relevant URLs — pages actually read come first."""
    seen = set()
    read_urls = []
    search_urls = []

    def add_url(target_list, raw_url):
        url = raw_url.strip().rstrip(",")
        if not url.startswith("http") or url in seen:
            return
        seen.add(url)
        target_list.append(url)

    for action, observation in intermediate_steps:
        if action.tool == "url_reader":
            tool_input = action.tool_input
            url = tool_input.get("url", "") if isinstance(tool_input, dict) else str(tool_input)
            add_url(read_urls, url)
            continue

        if action.tool != "web_search":
            continue

        for line in observation.split("\n"):
            line = line.strip()
            if line.startswith("Url:"):
                add_url(search_urls, line.replace("Url:", "", 1))
            else:
                match = re.search(r"https?://[^\s,]+", line)
                if match:
                    add_url(search_urls, match.group(0))

    return (read_urls + search_urls)[:max_sources]


# Create your views here.


@method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=False),name='post')
class ResearchView(APIView):

    permission_classes=[IsAuthenticated]

    @extend_schema(request=ResearchSerializer)
    def post(self, request):
        was_limited=getattr(request,'limited',False)
        # limited=is_ratelimited(request=request,
        #                        group='research_post',
        #                        key='user_or_ip',
        #                        rate='5/m',
        #                        increment=True
        #                        )

        if was_limited:
            return Response({'error':"Rate limit exceeded. Please wait before making another request."},
                            status=429)
        question=request.data.get('question')

        if not question:
            return Response({"error":"question is required"},status=400)

        session,created=ResearchSession.objects.get_or_create(
            user=request.user,
            defaults={'title':question[:50]}
        )

        past_queries=Query.objects.filter(session=session).order_by('-created_at')[:10]
        chat_history=""
        for q in past_queries:
            chat_history+=f"Human:{q.question}\nAssistant:{q.answer}\n\n"
        try:

            agent = get_agent(question,chat_history)

            answer=agent['output']
            sources = extract_sources(agent.get('intermediate_steps', []))

            Query.objects.create(
                session=session,
                question=question,
                answer=answer,
                sources=json.dumps(sources)
            )

            return Response({
    "answer": answer,
    "sources": sources
})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class HistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        session = ResearchSession.objects.filter(user=request.user).first()
        if session:
            all_queries = Query.objects.filter(session=session).order_by('created_at').values('id','question','answer','sources','created_at')
            return Response({"history":list(all_queries)})
        else:
            return Response({"history":[]})



class DeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self,request):
        session=ResearchSession.objects.filter(user=request.user).first()
        if session:
          Query.objects.filter(session=session).delete()
        return Response({"Query Session Deleted Successfully"})



def index_page(request):
    return render(request, 'agent/index.html')

@login_required
def chat_page(request):
    session = ResearchSession.objects.filter(user=request.user).first()
    queries = []
    if session:
        queries = Query.objects.filter(session=session).order_by('created_at')
    return render(request, 'agent/chat.html', {'queries': queries})

@login_required
def history_page(request):
    session = ResearchSession.objects.filter(user=request.user).first()
    queries = []
    if session:
        queries = Query.objects.filter(session=session).order_by('created_at')
    return render(request, 'agent/history.html', {'queries': queries})

@login_required
def clear_history(request):
    if request.method == 'POST':
        session = ResearchSession.objects.filter(user=request.user).first()
        if session:
            Query.objects.filter(session=session).delete()
    return redirect('history-page')
