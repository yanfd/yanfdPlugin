import matplotlib.pyplot as plt

labels = ['A', 'B', 'C', 'D']
sizes = [15, 30, 45, 10]

plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
plt.axis('equal')  # 保持饼图为圆形
plt.title('bingtu')
plt.savefig('pie_chart.png') #保存图片。
plt.show()