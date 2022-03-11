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

2. MySQL để lưu trữ dữ liệu heatmap sau phân tích 
 
3. Module visualize thông tin heatmap trên giao diện jupyter notebook
    - Jupyter Notebook
    - Matplotlib
    
### Hướng dẫn cài đặt môi trường:
1. Cài Anaconda: https://docs.anaconda.com/anaconda/install/index.html
2. Cài MySQL: 
- Windows/MacOS: https://dev.mysql.com/downloads/mysql/
- Ubuntu: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
        
   > sudo apt install mysql-server -y
        
   > sudo mysql_secure_installation
3. Tạo môi trường anaconda tên là heatmap
    > conda create -n heatmap python=3.9.7 -y
4. Kích hoạt môi trường heatmap: 
    > conda activate heatmap 
5. Cài các thư viện từ file requirements.txt
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


