import urllib.request as req
import bs4


class basicInfo:
    def __init__(self, MoodleSession):
        self.MoodleSession = MoodleSession
        self.headers = {
            "cookie": "MoodleSession=" + self.MoodleSession,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        self.profile_url = "https://ummoodle.um.edu.mo/user/profile.php"
    pass

    def get_all_basic_info(self):
        #url = self.profile_url
        request = req.Request(self.profile_url, headers=self.headers)
        ###發送請求
        with req.urlopen(request) as response:
            result = response.read().decode("utf-8")
        ###bs4分析頁面
        root_HTML = bs4.BeautifulSoup(result, "html.parser")
        result = root_HTML.select(".d-inline-block.aabtn img")
        icon_url = result[0]["src"]

        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")
        title_list = root_html.find_all("dt")
        title = root_html.find("dt", text='Email address')
        position = title_list.index(title)
        email = result[position].get_text()

        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")
        title_list = root_html.find_all("dt")
        title = root_html.find("dt", text='Student No.')
        position = title_list.index(title)
        student_no = result[position].get_text()

        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")

        try:
            title_list = root_html.find_all("dt")
            title = root_html.find("dt", text='Chinese Name')
            position = title_list.index(title)
            student_name = result[position].get_text()
        except Exception:
            root_html = self.full_HTML()
            result = root_html.select(".page-header-headings h1")
            student_name = result[0].get_text()

        result ={
            "icon_url":icon_url,
            "email":email,
            "student_no":student_no,
            "student_name":student_name
        }
        return result


    ##icon
    def get_icon_url(self):
        #url = self.profile_url
        request = req.Request(self.profile_url, headers=self.headers)
        ###發送請求
        with req.urlopen(request) as response:
            result = response.read().decode("utf-8")
        ###bs4分析頁面
        root_HTML = bs4.BeautifulSoup(result, "html.parser")
        result = root_HTML.select(".d-inline-block.aabtn img")
        return result[0]["src"]

    def download_icon(self,path,filename,img_url):
        #url = self.get_icon_url()
        request = req.Request(img_url, headers=self.headers)
        ###發送請求
        with req.urlopen(request) as file:
            file_data = file.read()
        open(path+filename+".jpg", "wb").write(file_data)
        print("DONE : download ummoodle icon")
        return path+filename+".jpg"



    ##text infomantion
    def full_HTML(self):
        #url = self.profile_url
        request = req.Request(self.profile_url, headers=self.headers)
        ###發送請求
        with req.urlopen(request) as response:
            result = response.read().decode("utf-8")
        ###bs4分析頁面
        root_HTML = bs4.BeautifulSoup(result, "html.parser")
        return root_HTML

    def cardbody_HTML(self):
        #url = self.profile_url
        request = req.Request(self.profile_url, headers=self.headers)
        ###發送請求
        with req.urlopen(request) as response:
            result = response.read().decode("utf-8")
        ###bs4分析頁面
        root_HTML = bs4.BeautifulSoup(result, "html.parser")
        result = root_HTML.select(".card-body")
        return result

    def get_student_email(self):
        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")

        title_list = root_html.find_all("dt")
        title = root_html.find("dt", text='Email address')
        position = title_list.index(title)

        return result[position].get_text()

    def get_student_no(self):
        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")

        title_list = root_html.find_all("dt")
        title = root_html.find("dt", text='Student No.')
        position = title_list.index(title)

        return result[position].get_text()

    def get_student_name(self):
        root_html = self.cardbody_HTML()[1]
        result = root_html.select(".contentnode dd")

        try:
            title_list = root_html.find_all("dt")
            title = root_html.find("dt", text='Chinese Name')
            position = title_list.index(title)
            return result[position].get_text()
        except Exception:
            root_html = self.full_HTML()
            result = root_html.select(".page-header-headings h1")
            return result[0].get_text()

        return "name_not_found"

    def get_header_name(self):
        root_html = self.full_HTML()
        result = root_html.select(".page-header-headings h1")
        return result[0].get_text()
