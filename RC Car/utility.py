import math
import numpy as np
import time



def Point_Left_Or_Right_From_Line(lineStart, lineEnd, point):
    #https://math.stackexchange.com/questions/274712/calculate-on-which-side-of-a-straight-line-is-a-given-point-located
    left_right = (point.x - lineStart.x) * (lineEnd.y - lineStart.y) - (point.y - lineStart.y) * (lineEnd.x - lineStart.x)
    ret = 0

    if abs(left_right) < 2:
      return ret

    if (left_right < 0):
      ret = -1
    elif (left_right > 0):
      ret = 1

    return ret

def current_milli_time():
    return round(time.time() * 1000)

def globalDirectionToLocal(worldDir, angle):
  rads = math.radians(angle)
  localX = math.cos(rads) * worldDir.x + math.sin(rads) * worldDir.y
  localY = -math.sin(rads) * worldDir.x + math.cos(rads) * worldDir.y
  return Vector2(localX, localY)

def globalPointToLocal(localCoords ,worldPt, angle):
  dist = worldPt - localCoords
  return globalDirectionToLocal(dist, angle)

def calc_side_slip(localVel):
  normed = localVel.normalize()
  rads = -math.atan2(normed.x, normed.y)
  return math.degrees(rads)

def remap(value, from_low, from_high, to_low, to_high):
  return np.interp(value,[from_low,from_high],[to_low,to_high])

def sanity_clip_one_to_minus_one(value):
  return np.clip(value, -1.0, 1.0)

def quaternion_to_euler_angle(w, x, y, z):
    #https://stackoverflow.com/questions/56207448/efficient-quaternions-to-euler-transformation
    #ysqr = y * y

    #t0 = +2.0 * (w * x + y * z)
    #t1 = +1.0 - 2.0 * (x * x + ysqr)
    #X = math.degrees(math.atan2(t0, t1))

    #t2 = +2.0 * (w * y - z * x)
    #t2 = +1.0 if t2 > +1.0 else t2
    #t2 = -1.0 if t2 < -1.0 else t2
    #Y = math.degrees(math.asin(t2))

    #t3 = +2.0 * (w * z + x * y)
    #t4 = +1.0 - 2.0 * (ysqr + z * z)
    #Z = math.degrees(math.atan2(t3, t4))

    #return X, Y, Z
    siny_cosp= 2 * (w*z+x+y)
    cosy_cosp= 1 - 2* (y*y + z*z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    #if yaw < 0:
    #    yaw=yaw + 2+ math.pi

    return yaw * (180/math.pi)


def project_point_onto_line(point, lineStart, lineEnd):
  rhs = point - lineStart;
  vector2 = lineEnd - lineStart;
  magnitude = vector2.get_length();
  lhs = vector2;
  if (magnitude > 0.00001):
    lhs = Vector2(lhs.x / magnitude, lhs.y / magnitude);
  num2 = clamp(Vector2.dot_product(lhs, rhs), 0, magnitude);
  return (lineStart + (lhs * num2));

def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value

def distance_point_to_line(point, lineStart, lineEnd):
  return (project_point_onto_line(point, lineStart, lineEnd) - point).get_length();

class Vector2:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    
  # Used for debugging. This method is called when you print an instance  
  def __str__(self):
    return "(" + str(self.x) + ", " + str(self.y) + ")"
    
  def get_length(self):
    return math.sqrt(self.x ** 2 + self.y ** 2)
    
  def __add__(self, v):
    return Vector2(self.x + v.x, self.y + v.y)
    
  def __sub__(self, v):
    return Vector2(self.x - v.x, self.y - v.y)

  def __mul__(self, n):
    return Vector2(self.x * n, self.y * n)
  def __rmul__(self, n):
    return self.__mul__(n)

  def normalize(self):
    length = self.get_length()
    return Vector2(self.x / length, self.y / length)

  @staticmethod
  def perpendicular(other):
    #counter clockwise
    #https://gamedev.stackexchange.com/questions/70075/how-can-i-find-the-perpendicular-to-a-2d-vector
    return Vector2(-other.y, other.x);

  @staticmethod
  def distance(p, q):
    return math.sqrt((q.x - p.x)**2 + (q.y - p.y)**2)  

    
  # def __div__(self, n):
  #   n /= -1
  #   return self * n
    
  @staticmethod
  def dot_product(v1, v2):
    return (v1.x * v2.x + v1.y * v2.y)
