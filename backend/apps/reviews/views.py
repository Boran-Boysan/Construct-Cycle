from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, ReviewVote
from .serializers import ReviewSerializer, ReviewCreateSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        qs = Review.objects.filter(is_approved=True)
        product = self.request.query_params.get('product')
        if product:
            qs = qs.filter(product_id=product)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        review = self.get_object()
        is_helpful = request.data.get('is_helpful', True)
        ReviewVote.objects.update_or_create(review=review, user=request.user, defaults={'is_helpful': is_helpful})
        review.helpful_count = review.votes.filter(is_helpful=True).count()
        review.save()
        return Response({'message': 'Oyunuz kaydedildi.'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        reviews = Review.objects.filter(user=request.user)
        return Response(ReviewSerializer(reviews, many=True).data)
