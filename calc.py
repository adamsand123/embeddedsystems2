values1=[]
values2=[]

with open("values1.txt") as f1:
	for line in f1:
		values1.append(line)

with open("values2.txt") as f2:
	for line in f2:
		values2.append(line)
avg=0
count=0
f=open("measure.txt","a")
for i in range(len(values1)):
#	print("Delay: " + str(float(values2[i])/1000) - str(float(values1[i])/1000) + " ms")
	delay=float(values2[i]) - float(values1[i])
	print(str(delay)+" sec")
	f.write(str(delay)+" sec"+"\n")
	avg+=delay
	count+=1

print("average delay: " + str(float(avg)/count) + " sec")

f.write("average delay: " + str(float(avg)/count) + " sec\n")
