from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.cache import cache

class IndexView(generic.ListView):
    template_name = "app/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "app/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "app/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "app/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def index(request):
    # Check if the list of questions is in the cache
    questions = cache.get('questions_list')

    if questions is None:
        # If not in the cache, fetch the list of questions from the database
        questions = Question.objects.order_by('-pub_date')[:5]

        # Store the list of questions in the cache for future use
        cache.set('questions_list', questions, timeout=300)  # Set a timeout in seconds (e.g., 5 minutes)

    context = {'latest_question_list': questions}
    return render(request, 'app/index.html', context)

def detail(request, question_id):
    # Check if the question is in the cache
    question = cache.get(f'question_{question_id}')

    if question is None:
        # If not in the cache, fetch the question from the database
        question = get_object_or_404(Question, pk=question_id)

        # Store the question in the cache for future use
        cache.set(f'question_{question_id}', question, timeout=300)  # Set a timeout in seconds (e.g., 5 minutes)

    context = {'question': question}
    return render(request, 'app/detail.html', context)
