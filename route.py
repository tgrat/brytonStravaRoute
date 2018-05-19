import re
import sys
import math
import fileinput
import sqlite3
import shutil
import string
# def uploadRoute(file)
    
def dist_lat_lon(file):
    with open(file,"r") as fi:
        i = 0
        dist = 0
        lat = []
        lon=  []
        for ln in fi:
            if ln.lstrip().startswith("<trkpt"):
                lat.append(math.radians(float(re.search("lat=\"(-?\d+.\d+)",ln).group(1))))
                lon.append(math.radians(float(re.search("lon=\"(-?\d+.\d+)",ln).group(1))))
                
                if i>0:
                    a = math.sin((lat[i]-lat[i-1])/2)*math.sin((lat[i]-lat[i-1])/2)+math.cos(lat[i-1])*math.cos(lat[i]) * math.sin((lon[i]-lon[i-1])/2) * math.sin((lon[i]-lon[i-1])/2)
                    b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    d = 6371e3*b
                    dist += d
                i += 1
    return dist, lat, lon

def change_format(file, routenum, dist, lat, lon):
    line = []
    flag = 0
    i = 0
    with open(file) as fi:
        for ln in fi:
            i += 1
            line.append(ln)

    i = 0
    with open(file) as fi:
        for ln in fi:
            i += 1
            if ln.lstrip().startswith("<trkpt"):
                trk = i
                print trk
                break

    with open("route-%s.gpx" %(str(routenum)),"w+") as fo:
        
        fo.write("<?xml version='1.0' encoding='utf-8'?>\n")
        fo.write("<gpx xmlns=\"http://www.brytonsport.com/BDX/2/2\" creator=\"bryton\" version=\"2.2.0.3\">\n")
        fo.write("<metadata>\n")
        fo.write("<name>%s</name>\n" %file)
        fo.write("<time/>\n")
        fo.write("<bounds minlat=\"%f\" minlon=\"%f\" maxlat=\"%f\" maxlon=\"%f\"/>\n" % (math.degrees(min(lat)), math.degrees(min(lon)), math.degrees(max(lat)), math.degrees(max(lon))))
        fo.write("<extensions>\n")
        fo.write("<sharetype>1</sharetype>\n")
        fo.write("<acttype subtype=\"0\">0</acttype>\n")
        fo.write("<trvDist>%f</trvDist>\n" %dist)
        fo.write("</extensions>\n")
        fo.write("</metadata>\n")
        fo.write("<rte>\n")
        fo.write("<number>2</number>\n")
        fo.write("<rtept lat=\"%f\" lon=\"%f\"/>\n" % (math.degrees(lat[0]), math.degrees(lon[0])))
        fo.write("<rtept lat=\"%f\" lon=\"%f\"/>\n" % (math.degrees(lat[len(lat)-1]), math.degrees(lon[len(lon)-1])))
        fo.write("</rte>\n")
        fo.write("<trk>\n")
        fo.write("<trkseg>\n")

        for i in xrange(trk-1,len(line)): #CHANGE
            fo.write("%s" %(line[i]))

            # if "<name>" in ln and flag==0:
            #   line.append("   <bounds minlat=\"%f\" minlon=\"%f\" maxlat=\"%f\" maxlon=\"%f\"/>\n" 
            #       % (math.degrees(min(lat)), 
            #           math.degrees(min(lon)), 
            #           math.degrees(max(lat)), 
            #           math.degrees(max(lon))))
            #   line.append("   <extensions>\n      <sharetype>1</sharetype>\n      <acttype subtype=\"0\">0</acttype>\n      <trvDist>%f</trvDist>\n   </extensions>" 
            #       %(dist))
            #   flag = 1
            # if "</metadata>" in ln:
            #   line.append("  <rte>\n      <number>2</number>\n      <rtept lat=\"%f\" lon=\"%f\"/>\n      <rtept lat=\"%f\" lon=\"%f\"/>\n   </rte>\n"
            #       %(math.degrees(lat[0]), math.degrees(lon[0]), math.degrees(lat[len(lat)-1]), math.degrees(lon[len(lon)-1])))

    # with open("route-%s.gpx" %(str(routenum)),"wa+") as fo:
    #   for i in xrange(len(line)):
    #       fo.write("%s" %(line[i]))
    
    return 0

def sql_last():
    conn = sqlite3.connect('/mnt/bryton/thalia/applications/CYCLING/DATA/ROUTE/route.dat')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM Route ORDER BY idRoute DESC LIMIT 1')
    r = c.fetchone()
    last = r['idRoute']

    conn.close()

    return last

def sql_insert(routenum,name,dist):
    conn = sqlite3.connect('/mnt/bryton/thalia/applications/CYCLING/DATA/ROUTE/route.dat')
    c = conn.cursor()
    data = {'idRoute' : str(routenum), 'Title' : str(name), 'TotalLength' : str(dist)}
    columns = ', '.join(map(str, data.keys()))
    values = ', '.join(map(repr, data.values()))
    c.execute("INSERT INTO Route ({}) VALUES ({})".format(columns, values))
    conn.commit()
    conn.close()

    return 0

if __name__ == '__main__':
    filename = sys.argv[1]
    routenum = sql_last()
    routenum += 1
    dist, lat, lon = dist_lat_lon(filename)
    change_format(filename,routenum,dist,lat,lon)
    sql_insert(routenum,filename,dist)
    shutil.copyfile('route-%s.gpx' %str(routenum),'/mnt/bryton/thalia/applications/CYCLING/DATA/ROUTE/route-%s.gpx' %str(routenum))
