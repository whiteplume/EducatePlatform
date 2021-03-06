# coding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from models import Course, CourseResource
from operation.models import UserFavorite, CourseComments

# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        # 课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 6, request=request)

        courses = p.page(page)
        return render(request, "course-list.html", {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses
        })


class CourseDetailView(View):
    # 课程详情页
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        course_has_fav = False
        org_has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                org_has_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                course_has_fav = True

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = []
        return render(request, 'course-detail.html', {
            "course": course,
            "relate_courses": relate_courses,
            "course_has_fav": course_has_fav,
            "org_has_fav": org_has_fav
        })


class CourseInfoView(View):
    # 课程章节信息
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            "course": course,
            "all_resources": all_resources,
        })


class CourseCommentsView(View):
    # 课程评论
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_comments = CourseComments.objects.all()
        return render(request, 'course-comment.html', {
            "course": course,
            "all_comments": all_comments,
        })


class AddCommentsView(View):
    # 用户添加课程评论
    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", 0)
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status": "success", "msg": "添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "添加失败"}', content_type='application/json')
