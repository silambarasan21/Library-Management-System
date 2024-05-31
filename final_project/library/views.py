from django.shortcuts import render
  
# Create your views here.
from django.db.models import Q
from django.shortcuts import render,redirect
from library.form import CustomUserForm
from library.models import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.http import HttpResponse,JsonResponse
from rest_framework.decorators import api_view
# from app.models import Book_Login
from django.contrib.auth import authenticate,login
from datetime import datetime, timedelta
from django.db import transaction

# Create your

# @views here.

def home(request):
    return render(request,'home.html')

def usersignup(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        query_dict = request.POST
        username = query_dict.get('username')
        email =  query_dict.get('email')
        if form.is_valid():
            form.save()
            admin_user = User.objects.filter(email=email).first()
            user_id = admin_user
            user_details = StudentDetails(username = username,email = email,user = user_id)
            user_details.save()
            return redirect('userlogin')
    return render(request,'usersignup.html',{'form':form})

def adminsignup(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        query_dict = request.POST
        username = query_dict.get('username')
        email =  query_dict.get('email')
        if form.is_valid():
            form.save()
            # admin_user = User.objects.filter(email=email).first()
            # user_id = admin_user
            # user_details = StudentDetails(username = username,email = email,user = user_id)
            # user_details.save()
            return redirect('adminlogin')
    return render(request,'adminsignup.html ',{'form':form})




def adminlogin(request):
    if request.method=='POST':
        name=request.POST.get('Name')
        pwd=request.POST.get('Password')
        try:
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                return redirect('Bookdetails')
            else:
                return redirect ('adminlogin')

        except:
            pass
    return render(request,'adminlogin.html')



def userlogin(request):
    if request.method=='POST':
        name=request.POST.get('Name')
        pwd=request.POST.get('Password')
        try:
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                user_id = request.user.id
            student=StudentDetails.objects.get(user_id = user_id)
            if student.status==1:
                return redirect('take')
            else:
                return redirect ('userlogin')

        except:
            pass
    return render(request,'userlogin.html')

def bookdetails(request):
    obj=BookDetails.objects.all()
    return render(request,'bookdetails.html',{'obj':obj})

def take(request):
    obj = BookDetails.objects.all()
    if request.method=='POST':
        aa=request.POST.get('search')
        bb=request.POST.get('searchcode')
        if bb =='':
            obj  = BookDetails.objects.filter(name=aa)
        if aa == '':
            obj = BookDetails.objects.filter(book_code=bb)
        
    return render(request,'take.html',{'obj':obj})


def lib(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            user_id = request.user.id
            date = datetime.now().date()
            library=BookDetails.objects.create(name=request.POST.get('Name'),book_code=request.POST.get('Code'),author_name=request.POST.get('Author'),
                                            date=request.POST.get('Date'),status=request.POST.get('Status'),amount=request.POST.get('Amount'),
                                            created_date=date,created_by=user_id,available_books = request.POST.get('available_books'),
                                            book_img = request.FILES['updatebook'])
    
            return redirect("Bookdetails")
        else:
            return redirect("book")
    return render(request, 'book.html')



def updatebook(request,pk):
    obj=BookDetails.objects.get(id=pk)
    if request.method=='POST':
        library = BookDetails.objects.filter(id=pk).first()
        library.name = request.POST.get('Name')
        library.book_code = request.POST.get('Code')
        library.author_name = request.POST.get('Author')
        library.date = request.POST.get('Date')
        library.amount = request.POST.get('Amount')
        library.available_books = request.POST.get('available_books')
        library.book_img = request.FILES['updatebook']
        date = datetime.now().date()
        library.updated_date = date
        library.save()
        return redirect('Bookdetails')
    return render(request,'updatebook.html',{'obj':obj})

def deletebook(request,pk):
    obj=BookDetails.objects.filter(id=pk)
    obj.delete()
    print("deleted")
    return redirect('Bookdetails')


@transaction.atomic()
def takebook(request,pk):
        if request.user.is_authenticated:
            user_id = request.user.id
            date = datetime.now().date()
            #Reduce amount in Useraccount
            book_id = pk
            book_details = BookDetails.objects.filter(id = book_id).first()
            if book_details.available_books != 0:
                book_name = book_details.name
                book_code = book_details.book_code
                book_price = book_details.amount
                book_quantity = book_details.available_books
                user_details = StudentDetails.objects.filter(user_id = user_id).first()
                #Amount Reduction
                user_amount = user_details.wallet_balance
                current_amount = user_amount - book_price
                user_details.wallet_balance = current_amount
                user_details.save()
                
                #Book History Registeration
                student = StudentDetails.objects.filter(user_id = user_id).first()
                student_id = student.id
                book_history = Booktransferhistory(student_id = student_id,code = book_code,
                                                    book_name = book_name,status = "Take")
                book_history.save()
                    
                #UserBookstatus Registeration
                status = UserBookStatus(student_id=student_id,book_id = book_id)
                status.save()

                #UserBookDetails Registeration
                user = UserBookDetails.objects.filter(student_id = student_id).first()
                if user is  None:
                    user_book_details = UserBookDetails(student_id = student_id,
                                                books_quantity = 1,updated_at = date)
                    user_book_details.save()
                else:
                    user_update = UserBookDetails.objects.filter(student_id = student_id).first()
                    books_quantity = user_update.books_quantity 
                    quantity = int(books_quantity) +1
                    user_update.books_quantity = quantity
                    user_update.save()

                #Books reduction in BookDetails
                book_details = BookDetails.objects.filter(id = book_id).first()
                quantity = book_details.available_books
                quantity-=1

                book_details.available_books = quantity
                if quantity == 0:
                    book_details.status = 'Unavailable'
                book_details.save()
            else:
                print("No stocks")
            return redirect('take')
        
@transaction.atomic()
def retainbook(request,pk):
    if request.user.is_authenticated:
        user_id = request.user.id
        book_id = pk
        student = StudentDetails.objects.filter(user_id = user_id).first()
        student_id = student.id
        user_book = UserBookStatus.objects.filter(student_id=student_id,book_id=book_id).first()
        if user_book is not None:
            if user_book.status == 1:
                date = datetime.now().date()
                    
                #Details
                book_details = BookDetails.objects.filter(id = book_id).first()
                book_name = book_details.name
                book_code = book_details.book_code
                book_price = book_details.amount
                book_quantity = book_details.available_books

                #Book History Registeration
                student = StudentDetails.objects.filter(user_id = user_id).first()
                student_id = student.id
                book_history = Booktransferhistory(student_id = student_id,code = book_code,
                                                    book_name = book_name,status = "Return")
                book_history.save()

                # books reduction
                books_reduction = UserBookDetails.objects.filter(student_id = student_id).first()
                book_quantity = books_reduction.books_quantity
                quantity = book_quantity-1
                books_reduction.books_quantity = quantity
                books_reduction.save()

                #books updation
                book_details = BookDetails.objects.filter(id = book_id).first()
                quantity = book_details.available_books
                quantity+=1
                book_details.available_books = quantity
                if quantity !=0:
                    book_details.status = 'Available'
                book_details.save()
                user_book.status = 0
                user_book.delete()
            else:
                print("you dont have book so you are not able to return")

        else:
            print("please purchase book")


                
    return redirect('take')

