from datetime import datetime

date1 = datetime.strptime("23.12.20", "%d.%m.%y")
date2 = datetime.strptime("30.11.20", "%d.%m.%y")

dates = {1:date1, 2:date2}
print(max(dates.values()))