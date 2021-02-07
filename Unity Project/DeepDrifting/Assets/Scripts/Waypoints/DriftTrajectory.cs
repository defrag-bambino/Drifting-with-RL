
using System.Collections.Generic;
using UnityEngine;
using PathCreation;

public class DriftTrajectory : MonoBehaviour
{
    private PathCreator pathCreator;
    private VertexPath path;

    public float WaypointSpacing = 5;
    private float travelledDistanceOnPath = 0;

    //public GameObject WaypointMarker;

    private LineRenderer line;

    private Vector3 currentWaypointOrthgLineStart;
    private Vector3 currentWaypointOrthgLineEnd;


    private int directionFactor = 1;

    private float MaxDistFromPath;


    // Start is called before the first frame update
    private void init()
    {
        //retrieve the path object
        pathCreator = GetComponent<PathCreator>();
        path = pathCreator.path;

        //draw a line to see the path
        line = pathCreator.gameObject.AddComponent<LineRenderer>();
        line.useWorldSpace = false;
        line.startWidth = 1f;
        line.endWidth = 1f;
        line.positionCount = path.localPoints.Length;
        line.SetPositions(path.localPoints);
    }



    public void drawWpLines(Transform carPos, int amountOfNxtWps)
    {
        //perpendicular line
        Debug.DrawLine(currentWaypointOrthgLineStart, currentWaypointOrthgLineEnd, Color.red);

        //car to path
        Debug.DrawLine(carPos.position, PathMathSupports.ProjectPointLine(carPos.position, getWaypointRelativeToCurrent(-1), getWaypointRelativeToCurrent(0)), Color.green);

        //next WPs
        for (int i = 0; i < amountOfNxtWps; i++)
        {
            Debug.DrawLine(carPos.position, getWaypointRelativeToCurrent(i), Color.blue);
        }
    }

    public void reset(float maxDistFromPath){
        init();
        MaxDistFromPath = maxDistFromPath;

        //randomly switch between driving the path forwards and backwards
        if(Random.Range(0,2) == 0) directionFactor = 1;
        else directionFactor = -1;

        //set the current waypoint to a random one along the whole path
        travelledDistanceOnPath = Random.Range(0, (int) path.length * WaypointSpacing);        
        switchToNextWaypoint();
    }

    public float getDistOfCarToCurrWpOrthgLine(Transform carTrans){
        //WaypointMarker.transform.position = currentWaypoint + Vector3.up;
        return PathMathSupports.DistancePointLine(carTrans.position, currentWaypointOrthgLineStart, currentWaypointOrthgLineEnd);
    }

    public float getDistOfCarToPath(Transform carPos){
        //This assumes the car is always between the current and last waypoint.
        //This assumption allows us to project the cars position onto the line ranging from last to current waypoint
        //and calculate the distance to that line
        return PathMathSupports.DistancePointLine(carPos.position, getWaypointRelativeToCurrent(-1), getWaypointRelativeToCurrent(0));
    }

    public float getDistOfCarToOrthgLineWhilePassing(Transform carPos){
        //This projects the position of the car onto the orthg line (sort of like a shadow of the car onto the finish line)
        //and then calculates the distance from the projected position to the center of the orthg line (where the current waypoint is)
        return Vector3.Distance(PathMathSupports.ProjectPointLine(carPos.position, currentWaypointOrthgLineStart, currentWaypointOrthgLineEnd), getWaypointRelativeToCurrent(0));
    }


    public void switchToNextWaypoint(){
        travelledDistanceOnPath = PathMathSupports.nfmod(travelledDistanceOnPath + WaypointSpacing, path.length);

        //calc the new orthg line
        var values = PathMathSupports.calculateCurrentOrthogonalLine(getWaypointRelativeToCurrent(-1), getWaypointRelativeToCurrent(0), MaxDistFromPath);
        currentWaypointOrthgLineStart = values.Item1;
        currentWaypointOrthgLineEnd = values.Item2;
    }


    public Vector3 getWaypointRelativeToCurrent(int increment){
        float pointDist = PathMathSupports.nfmod(travelledDistanceOnPath + (increment * WaypointSpacing), path.length); //stay within bounds
        return path.GetPointAtDistance(directionFactor * pointDist);
    }



}
