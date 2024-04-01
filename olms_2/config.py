"""
作者：Samoyed320
时间：2023/04/22
代码功能：api接口配置
"""

grant_type = 'client_credentials'

client_id = 'Bf9MvfEn3OWA77zxfcANGKrN'
client_secret = 'zLY0F2zG0zbA1dmRYARfQpUUsjOwXI0B'

HOST = 'https://aip.baidubce.com/oauth/2.0/token?' \
       'grant_type=' + grant_type + \
       '&client_id=' + client_id + \
       '&client_secret=' + client_secret


Group_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getlist"
Group_add_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/add"
Group_delete_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/delete"
Add_user_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
Get_users_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/group/getusers"
Get_usernames_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/get"
Updata_user_ulr = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/update"
Detect_face_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
Search_face_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
Delete_face_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete"
Face_list_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/getlist"
