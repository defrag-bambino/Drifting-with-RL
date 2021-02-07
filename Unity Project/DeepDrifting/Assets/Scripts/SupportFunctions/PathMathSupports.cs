using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public static class PathMathSupports
{
    
    public static int PointLeftOrRightFromLine(Vector3 lineStart, Vector3 lineEnd, Vector3 point){
        //https://math.stackexchange.com/questions/274712/calculate-on-which-side-of-a-straight-line-is-a-given-point-located
        Vector2 start = new Vector2(lineStart.x, lineStart.z);
        Vector2 end = new Vector2(lineEnd.x, lineEnd.z);
        Vector2 pnt = new Vector2(point.x, point.z);

        float left_right = (pnt.x - start.x) * (end.y - start.y) - (pnt.y - start.y) * (end.x - start.x);
        int ret = 0;

        if(Mathf.Abs(left_right) < 3f) return ret;

        if (left_right < 0) ret = -1; 
        else if (left_right > 0) ret = 1; 

        return ret;
    }

    public static float nfmod(float a, float b){
        //negative float modulo
        return a - b * Mathf.Floor(a / b);
    }



    public static float DistancePointLine(Vector3 point, Vector3 lineStart, Vector3 lineEnd)
        {
            point.y = 0;
            lineStart.y = 0;
            lineEnd.y = 0;
            return Vector3.Magnitude(ProjectPointLine(point, lineStart, lineEnd) - point);
    }


    public static Vector3 ProjectPointLine(Vector3 point, Vector3 lineStart, Vector3 lineEnd)
        {
            Vector3 rhs = point - lineStart;
            Vector3 vector2 = lineEnd - lineStart;
            float magnitude = vector2.magnitude;
            Vector3 lhs = vector2;
            if (magnitude > 1E-06f)
            {
                lhs = (Vector3)(lhs / magnitude);
            }
            float num2 = Mathf.Clamp(Vector3.Dot(lhs, rhs), 0f, magnitude);
            return (lineStart + ((Vector3)(lhs * num2)));
    }


    public static (Vector3, Vector3) calculateCurrentOrthogonalLine(Vector3 start, Vector3 end, float HalfLength){
        Vector2 start2 = new Vector2(start.x, start.z);
        Vector2 end2 = new Vector2(end.x, end.z);

        Vector2 dir = (end2 - start2).normalized;
        Vector2 orthg = Vector2.Perpendicular(dir);
        Vector3 orthg3 = new Vector3(orthg.x, 0f, orthg.y);

        return (end + ( -HalfLength *  orthg3), end + ( HalfLength *  orthg3));
    }
    


    // public static float calcLocalPathCurvature(){
    //     var cc = CircleCenterFrom3Points(getWaypointRelativeToCurrent(-1), currentWaypoint, getWaypointRelativeToCurrent(1));
    //     var radius = (cc - new Vector2(currentWaypoint.x, currentWaypoint.z)).magnitude;
    //     radius = Mathf.Max(radius, 0.0001f);
    //     return 1f / radius;
    // }

     /**
  * Finds the center of the circle passing through the points p1, p2 and p3.
  * (NaN, NaN) will be returned if the points are colinear.
  */
    public static Vector2 CircleCenterFrom3Points (Vector3 p1, Vector3 p2, Vector3 p3) {
        p1.y = p2.y = p3.y = 0;
        float temp = p2.sqrMagnitude;
        float bc = (p1.sqrMagnitude - temp)/2.0f;
        float cd = (temp - p3.sqrMagnitude)/2.0f;
        float det = (p1.x-p2.x)*(p2.z-p3.z)-(p2.x-p3.x)*(p1.z-p2.z);
        if (Mathf.Abs(det) < 1.0e-6) {
            return new Vector2(float.NaN, float.NaN);
        }
        det = 1/det;
        return new Vector2((bc*(p2.z-p3.z)-cd*(p1.z-p2.z))*det, ((p1.x-p2.x)*cd-(p2.x-p3.x)*bc)*det);
 }


    public static float Remap(float value, float fromMin, float fromMax, float toMin, float toMax)
    {
        var fromAbs = value - fromMin;
        var fromMaxAbs = fromMax - fromMin;

        var normal = fromAbs / fromMaxAbs;

        var toMaxAbs = toMax - toMin;
        var toAbs = toMaxAbs * normal;

        var to = toAbs + toMin;

        return to;
    }


}
