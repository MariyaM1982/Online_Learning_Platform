from rest_framework.pagination import PageNumberPagination


class CourseLessonPagination(PageNumberPagination):
    """
    Пагинация для курсов и уроков
    Позволяет пользователю управлять размером страницы
    """
    page_size = 5  # Количество объектов на одной странице
    page_size_query_param = 'page_size'  # Позволяет менять размер страницы через параметр
    max_page_size = 20  # Максимальное количество объектов на странице