from django.http import JsonResponse
from django.conf import settings
from http import HTTPStatus
from rest_framework.decorators import api_view
from newsfinder.models import News, Channel
from .serializers import NewsSerializer, ListNewsSerializer, ChannelSerializer
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import requests

# params to generate docs using drf-yasg
param_channel_name = openapi.Parameter('channel_name', openapi.IN_QUERY, description="channel name eg.science",
                                       type=openapi.TYPE_STRING)
param_word_count = openapi.Parameter('word_count', openapi.IN_QUERY, description="word count range eg. 1-100",
                                     type=openapi.TYPE_STRING)
param_page = openapi.Parameter('page', openapi.IN_QUERY, description="page number eg. 1",
                               type=openapi.TYPE_NUMBER)
param_page_size = openapi.Parameter('page_size', openapi.IN_QUERY, description="number of items in one page eg. 10",
                                    type=openapi.TYPE_NUMBER)
param_source = openapi.Parameter('source', openapi.IN_QUERY, description="news source eg. cnn",
                                 type=openapi.TYPE_STRING)
list_news_response = openapi.Response('response', ListNewsSerializer)

list_channel_response = openapi.Response('response', ChannelSerializer)


# for the docs
@swagger_auto_schema(method='get',
                     manual_parameters=[param_channel_name,
                                        param_word_count, param_page,
                                        param_page_size, param_source],
                     responses={200: list_news_response})
@swagger_auto_schema(method='post', request_body=NewsSerializer)
@api_view(['GET', 'POST'])
def news_view(request) -> JsonResponse:
    """
    Api view for managing news operations.
    """
    if request.method == 'GET':
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
        except ValueError as e:
            return JsonResponse({'error': e.args[0]}, safe=False, status=HTTPStatus.BAD_REQUEST)
        params = {"language": "en", "page_size": page_size, "page": page}
        category = request.query_params.get('channel_name')
        source = request.query_params.get('source')
        word_count = request.query_params.get('word_count')
        if category:
            try:
                channel = Channel.objects.get(name=category)
            except Channel.DoesNotExist:
                return JsonResponse({'Not Found': 'Please provide valid channel_name in query.'},
                                    status=HTTPStatus.NOT_FOUND)
            params['category'] = category

        if source:
            params['sources'] = source

        # if word count is provided in query it will fetch and filter data from our database
        if word_count:
            if '-' not in word_count:
                return JsonResponse({'error': 'word_count should be in range eg. 0-100'}, status=HTTPStatus.BAD_REQUEST)
            try:
                min_limit = int(word_count.split('-')[0])
                max_limit = int(word_count.split('-')[1])
            except ValueError as e:
                return JsonResponse({'error': e.args[0]}, safe=False, status=HTTPStatus.BAD_REQUEST)
            qs = News.objects.filter(word_count__range=(min_limit, max_limit))
            serializer = ListNewsSerializer(qs, many=True)
        else:
            # if other query params are provided except word_count then it fetches from newsapi and saves in our db
            newsapi = NewsApiClient(api_key=settings.API_KEY)
            try:
                top_headlines = newsapi.get_top_headlines(**params)
            except Exception as e:
                return JsonResponse({'error': e.args[0].replace('category', 'channel')}, safe=False,
                                    status=HTTPStatus.INTERNAL_SERVER_ERROR)
            articles = top_headlines.get('articles')
            articles_list = []

            for article in articles:
                data = {
                    'channel': channel.id if category else None,
                    'channel_name': channel.name if category else None,
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'content': article.get('content'),
                    'published_date': article.get('publishedAt'),
                    'source': article['source']['id'] if article.get('source') else None
                }
                if data['url'] and data['title'] and data['content']:
                    # we later use articles_list to show response serialized by ListNewsSerializer
                    articles_list.append(data)
                    news_serializer = NewsSerializer(data=data)
                    if not news_serializer.is_valid():
                        return JsonResponse(news_serializer.errors, status=HTTPStatus.BAD_REQUEST)
                    qs = News.objects.filter(url=data['url'])
                    # if url doesn't exist in our database then its new data, save it
                    if not qs.exists():
                        news_serializer.save()

            serializer = ListNewsSerializer(data=articles_list, many=True)
            if not serializer.is_valid():
                return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)

        return JsonResponse(serializer.data, safe=False, status=HTTPStatus.OK)

    elif request.method == 'POST':
        serializer = NewsSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        data = serializer.validated_data
        url = data.get('url')
        data['word_count'] = get_word_count(url)

        qs = News.objects.filter(url=url)
        if not qs.exists():
            News(**data).save()
        else:
            qs.update(word_count=data['word_count'])

        return JsonResponse(NewsSerializer(qs, many=True).data, safe=False, status=HTTPStatus.CREATED)


@swagger_auto_schema(method='post', request_body=ChannelSerializer)
@swagger_auto_schema(method='get', responses={200: list_channel_response})
@api_view(['GET', 'POST'])
def channels_view(request) -> JsonResponse:
    """
    Api view for managing channels operations.
    """
    if request.method == 'POST':
        serializer = ChannelSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        try:
            Channel.objects.get(name=serializer.validated_data.get('name'))
        except Channel.DoesNotExist:
            # save channel name to database
            serializer.save()
        return JsonResponse(serializer.data, status=HTTPStatus.CREATED)

    elif request.method == 'GET':
        queryset = Channel.objects.all()
        serializer = ChannelSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['DELETE'])
def channels_detail_view(request, pk) -> JsonResponse:
    """
    Api view for channel delete operations.
    """
    if request.method == 'DELETE':
        try:
            channel = Channel.objects.get(pk=pk)
        except Channel.DoesNotExist:
            return JsonResponse({'Not Found': "Channel doesn't exist in database"}, status=HTTPStatus.NOT_FOUND)
        channel.delete()
        return JsonResponse({'message': 'Success'}, status=HTTPStatus.NO_CONTENT)


def get_word_count(url: str) -> int:
    """
    Fetch the text from url and count the total words
    in the page excluding html tags.
    """
    try:
        f = requests.get(url)
    except Exception:
        # error in fetching url, cannot count words
        return 0
    texts = None
    if f.text:
        soup = BeautifulSoup(f.text, 'html.parser')
        texts = soup.find_all(text=True)
    full_text_list = []
    exclude_list = [
        '[document]',
        'script',
        'noscript',
        'html',
        'header',
        'head',
        'meta',
        'img',
        'input'
    ]

    for txt in texts:
        if txt.parent.name not in exclude_list:
            full_text_list += txt
    word_count = len(full_text_list)

    return word_count
