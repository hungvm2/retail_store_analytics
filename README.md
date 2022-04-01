# Heatmap Project
### Heatmap Project gồm có 3 thành phần chính:
- Module xử lý luồng video và sinh ra dữ liệu heatmap
- Module visualize thông tin heatmap trên giao diện web

### Chi tiết công nghệ của từng thành phần:

1. Module xử lý luồng video, sinh ra dữ liệu heatmap 
    - OpenCV để đọc luồng 
    - Yolov4 để detect người trong khung hình 
    - SORT để tracking các đối tượng người trong khung hình 
    - Logic lưu trữ data vị trí trọng tâm của từng người trong khung hình vào file dữ liệu 

2. MySQL để lưu trữ dữ liệu heatmap sau phân tích, MySQL Workbench để thao tác với DB từ GUI 
 
3. Module visualize thông tin heatmap trên giao diện jupyter notebook
    - Jupyter Notebook
    - Matplotlib
    
### Hướng dẫn cài đặt môi trường:
1.Cài Anaconda: https://docs.anaconda.com/anaconda/install/index.html
2.Cài MySQL và MySQL Workbench: 
- Windows/MacOS: 
    - MySQL Community: https://dev.mysql.com/downloads/mysql/
    - MySQL Workbench GUI: https://dev.mysql.com/downloads/workbench/ 
- Ubuntu: https://linuxhint.com/installing_mysql_workbench_ubuntu/
    - Download mysql apt repo config
    - Update apt 
    > sudo apt update
    - MySQL server: 
    > sudo apt install mysql-server -y
    - Setup MySQL: 
    > sudo mysql_secure_installation
    - Setup Guide:
        - password validation: LOW
        - temporary password for root: 123456
        - continue with password provide: Yes
        - remove anonymous users: No
        - Disallow root login remotely: No
        - Remove test database: No
        - Reload privilege tables: Yes
    - Thay đổi root password tuân theo policy "abcd@1234":
        > sudo mysql 
        > ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'abcd@1234';
    - Tạo Database                  
        > create retail_store_analytics;
    - Import các tables:
        > use retail_store_analytics;
        > source <path_url.sql>
    - Cài MySQL Workbench để thao tác với MySQL server từ giao diện:
    > sudo apt install mysql-workbench-community
    - Mở MySQL Workbench
    > sudo mysql-workbench

3.Tạo môi trường anaconda tên là heatmap
  > conda create -n heatmap python=3.9.7 -y
    
4.Kích hoạt môi trường heatmap: 
  > conda activate heatmap 

5.Cài các thư viện từ file requirements.txt
  > pip install ./requirements.txt

### References:
```
@misc{pytorch-YOLOv4,
  author = {Tianxiaomo},
  title = {Pytorch-YOLOv4},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Tianxiaomo/pytorch-YOLOv4}},
  commit = {a65d219f9066bae4e12003bd7cdc04531860c672}
}
```

```
@inproceedings{Bewley2016_sort,
  author={Bewley, Alex and Ge, Zongyuan and Ott, Lionel and Ramos, Fabio and Upcroft, Ben},
  booktitle={2016 IEEE International Conference on Image Processing (ICIP)},
  title={Simple online and realtime tracking},
  year={2016},
  pages={3464-3468},
  keywords={Benchmark testing;Complexity theory;Detectors;Kalman filters;Target tracking;Visualization;Computer Vision;Data Association;Detection;Multiple Object Tracking},
  doi={10.1109/ICIP.2016.7533003}
}
```