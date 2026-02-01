from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
from lms.models import Course
from django.contrib.auth.mixins import LoginRequiredMixin

stripe.api_key = settings.STRIPE_API_KEY


@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(LoginRequiredMixin, View):
    """
    Создаёт сессию оплаты для курса
    """

    def post(self, request, *args, **kwargs):
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)

        # 1. Создаём продукт (если ещё не создан)
        try:
            product = stripe.Product.create(name=course.title)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # 2. Создаём цену
        try:
            price = stripe.Price.create(
                currency='usd',
                unit_amount=2000,  # $20.00
                product=product.id,
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # 3. Создаём сессию
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment-success/'),
                cancel_url=request.build_absolute_uri('/payment-cancel/'),
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'id': session.id, 'url': session.url})