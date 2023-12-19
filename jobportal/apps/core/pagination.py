class CustomPagination:
    start = 0
    limit = 4


    def get_last_page(self, view):
        print('view...',view)
        quotient = view.get_queryset().count() / self.limit
        print('quotient...',type(quotient))
        if isinstance(quotient, float):
            last_page = int(quotient) + 1
            print(last_page)
        else:
            last_page = quotient
        return last_page

    def get_pagination_indexes(self, view):
        page_number = view.request.GET.get("page")
        print("page_number...", page_number)
        print('view of pagination_indexes...',view)
        if page_number is not None:
            try:
                page_number = int(page_number)
            except ValueError:
                return self.start, self.limit
            last_page = self.get_last_page(view)
            print("lastpage...",last_page)
            if page_number > last_page:
                page_number = last_page
            return (self.limit*(page_number-1), self.limit*page_number) if page_number > 0 else (self.start, self.limit)
        return self.start, self.limit

    def get_paginated_qs(self, views):
        print("self...",self)
        print("views of get_paginated_qs....",views)
        start, end = self.get_pagination_indexes(views)
        print("start and end",start,end)
        return views.get_queryset()[start: end]

    @staticmethod
    def get_current_page(view):
        print("view",view.request)
        page = view.request.GET.get('page')
        default_active = "one"
        if page is not None:
            try:
                page = int(page)
                print("page...",page)
            except ValueError:
                return 1, default_active
            if page <= 0:
                print("page...",page)
                return page, "prev"
            if page > 3:
                print("page...",page)
                return page, "next"
            else:
                mapper = {1: "one", 2: "two", 3: "three"}
                print("mapper...",mapper)
                return page, mapper[page]
        return 1, default_active

    @staticmethod
    def get_nested_pagination(qs, nested_size): # [obj1, obj2, obj3, obj4]
        print("qs...",qs)
        print("nested_size...",nested_size)
        all_data = []
        each_data = list()
        for index, each in enumerate(qs, start=1):
            each_data.append(each)
            if index % nested_size == 0:
                print("Index...",index)
                all_data.append(each_data)
                each_data = list()
        if each_data:
            all_data.append(each_data)
        return all_data #  [[obj1, obj2], [obj3, obj4]]
    
