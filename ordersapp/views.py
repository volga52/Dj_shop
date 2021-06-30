from django.forms import inlineformset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from ordersapp.forms import OrderItemEditForm
from ordersapp.models import Order, OrderItem


class OrderList(ListView):
    model = Order

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_active=True)


class OrderCreate(CreateView):
    model = Order
    success_url = reverse_lazy('order:list')
    fields = []

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            formset = OrderFormSet()
        data['orderitems'] = formset
        return data


class OrderUpdate(UpdateView):
    pass


class OrderDelete(DeleteView):
    pass


class OrderRead(DetailView):
    pass


def forming_complete(request, pk):
    pass
