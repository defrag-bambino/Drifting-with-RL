using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using VehiclePhysics;

public class DriftAgent_new_rew_func: Agent
{

    public float MaxDistFromPath = 5f;

    private Rigidbody rb;

    public DriftTrajectory[] trajectories;
    private DriftTrajectory traj;//currently selected trajectory


    private VehiclePhysics.VPStandardInput VPinput;
    private VehiclePhysics.VPVehicleController VPcontrol;
    private VehiclePhysics.VehicleBase VPbase;

    private MeasurementUnit imu;

    public int NextKnownWaypoints = 5;//how many WPs to feed into the network (adjust num. of observations accordingly)

    private float CurrentSteerDirection;

    public float SteerSpeedDegPerSec = 100;//60° * pi/180 = 1,047rad

    public GameObject PointPopupPrefab;

    public float TireFrictionRandomMin = 0.8f;
    public float TireFrictionRandomMax = 1.5f;



    void Awake()
    {
        //cache all later requiered components
        VPcontrol = GetComponent<VehiclePhysics.VPVehicleController>();
        VPinput = GetComponent<VehiclePhysics.VPStandardInput>();
        VPbase = GetComponent<VehiclePhysics.VehicleBase>();
        rb = GetComponent<Rigidbody>();
        imu = GetComponent<MeasurementUnit>();
    }

    public override void OnEpisodeBegin()
    {
        if(traj) Destroy(traj.gameObject);
        traj = Instantiate(trajectories[Random.Range(0,trajectories.Length)]);

        //reset the trajectory object
        traj.reset(MaxDistFromPath);

        //reset the agent
        this.transform.position = traj.getWaypointRelativeToCurrent(-1);
        this.transform.LookAt(traj.getWaypointRelativeToCurrent(0));


        rb.angularVelocity = Vector3.zero;
        rb.velocity = Vector3.zero;
        rb.ResetInertiaTensor();//does this do anything?
        

        VehiclePhysics.VPResetVehicle.ResetVehicle(VPbase, 0f);
        VPcontrol.data.Set(Channel.Input, InputData.ManualGear, 1);

        randomizeTireFriction();
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        Vector3 localVel = imu.LocalVelocity;
        Vector2 localVelXZ = new Vector2(localVel.x, localVel.z);
        sensor.AddObservation(localVelXZ / 300f);

        sensor.AddObservation(-rb.angularVelocity.y / 10f);

        sensor.AddObservation(Mathf.Abs(imu.SideSlip) / 180f);

        Vector3 nextWP;
        Vector2 nextWP2;
        float maxWPdist = NextKnownWaypoints * traj.WaypointSpacing;
        for (int i = 0; i < NextKnownWaypoints; i++)
        {
            nextWP = transform.InverseTransformPoint(traj.getWaypointRelativeToCurrent(i));
            //Debug.DrawLine(car.transform.position, RaceTrack.getWaypointRelativeToCurrent(i), Color.green);
            nextWP2 = new Vector2(nextWP.x / maxWPdist, nextWP.z / maxWPdist); //normalize to [0,1]

            sensor.AddObservation(nextWP2);
        }

        sensor.AddObservation(VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / (1000.0f * VPcontrol.engine.maxRpm ));
        sensor.AddObservation(traj.getDistOfCarToPath(transform) / MaxDistFromPath);
        //sensor.AddObservation(CurrentSteerDirection);
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        //if( VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / 1000.0f > 4500f ) VPcontrol.data.Set(Channel.Input, InputData.ManualGear, 2);
        //if( VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / 1000.0f < 2000f ) VPcontrol.data.Set(Channel.Input, InputData.ManualGear, 1);

        if (vectorAction[0] == 0f){
            //VPinput.externalSteer = SmoothSteering(imu.SideSlip / VPcontrol.steering.maxSteerAngle); //Gyro
            VPinput.externalSteer = SmoothSteering(-rb.angularVelocity.y * 0.030516f);        //mapping to degrees per second);
        }
        else{
            VPinput.externalSteer = SmoothSteering(vectorAction[0]);
        }
        

        //Debug.Log(rb.angularVelocity.y);

        //VPinput.externalThrottle = PathMathSupports.Remap(vectorAction[1], -1f, 1f, 0f, 1f);
        VPinput.externalThrottle += vectorAction[1] * 0.05f;
        VPinput.externalThrottle = Mathf.Clamp(VPinput.externalThrottle, 0f, 1f);
        //if (VPinput.externalThrottle <= 0.1){
            //VPinput.externalHandbrake = 1;
        //}else{
            //VPinput.externalHandbrake = 0f;
        //}


        if (traj.getDistOfCarToPath(this.transform) >= MaxDistFromPath) //|| Mathf.Abs(imu.SideSlip) > 110f)
        {
            //print("too far from path, resetting..." + traj.getDistOfCarToPath(this.transform));
            SetReward(-10f);
            EndEpisode();
        }


        traj.drawWpLines(this.transform, NextKnownWaypoints);

        float rew = 0.0f;//-0.0001f;
        //TODO: Add a term that penalizes changes in sideslip angle, to make the drift more smooth. e.g. use slipangle derivative.

        int desiredAngleSign = PathMathSupports.PointLeftOrRightFromLine(traj.getWaypointRelativeToCurrent(-1), traj.getWaypointRelativeToCurrent(1), traj.getWaypointRelativeToCurrent(0));
        int currentAngleSign = (int)Mathf.Sign(imu.SideSlip);
        float PathCurvatureFactor;
        if(desiredAngleSign != 0 && desiredAngleSign == currentAngleSign) PathCurvatureFactor = 1f;//print("desired");
        else if(desiredAngleSign != 0 && desiredAngleSign != currentAngleSign) PathCurvatureFactor = -0.01f;//print("not desired");
        else PathCurvatureFactor = 1f;//print("dont care");


        float dist_to_orthL_rew = 1 - Mathf.Pow((traj.getDistOfCarToCurrWpOrthgLine(this.transform) / traj.WaypointSpacing), 0.4f);
        float dist_to_path_rew = 1 - Mathf.Pow((traj.getDistOfCarToPath(this.transform) / MaxDistFromPath), 0.4f);
        float slipangle_rew = (1f / (1f + Mathf.Pow(Mathf.Abs((Mathf.Abs(imu.SideSlip) - 55f) / 20f),(2f*1.5f)))) * PathCurvatureFactor;

        rew = 0.25f * dist_to_orthL_rew + 0.25f * dist_to_path_rew + 0.5f * slipangle_rew;


        if(traj.getDistOfCarToCurrWpOrthgLine(this.transform) <= 0.2f){

                //rew += 18f/20f * (Mathf.Abs(imu.SideSlip) / 90f) * PathCurvatureFactor;
                //float wp_passing_rew = 1f; 
                //https://www.wolframalpha.com/input/?i=plot+1%2F+%281+%2B+abs%28%28x-c%29%2Fa%29%5E%282b%29%29+for+a%3D15%2Cb%3D1.5%2Cc%3D50+from+x%3D0+to+90
                traj.switchToNextWaypoint();
                Instantiate(PointPopupPrefab, transform.position, Camera.main.transform.rotation).GetComponent<pointPopup>().display(rew);


                //quick and dirty way of display current tire friction. I should probably make a nice GUI display on screen...
                Instantiate(PointPopupPrefab, traj.transform.position, Camera.main.transform.rotation).GetComponent<pointPopup>().display(VPcontrol.tireFriction.settings.peak.y);
            }
            

        

        SetReward(rew);
        //show reward above car
        
        //print(rew);
        
        //}

        
    }

    private void randomizeTireFriction(){
        //based on the initial parametric tire friction model that edys vehicle physics came with.
        //this just shifts the curve up and down randomly
        float newVal = Random.Range(TireFrictionRandomMin, TireFrictionRandomMax);
        VPcontrol.tireFriction.settings.peak = new Vector2(2.0f, newVal);
        VPcontrol.tireFriction.settings.adherent = new Vector2(0.5f, newVal - 0.4f);
        VPcontrol.tireFriction.settings.limit = new Vector2(12.0f, newVal - 0.25f);
    }

    public override void Heuristic(float[] actionsOut)
    {
        //steer
        actionsOut[0] = 0f;
        if( Input.GetKey(KeyCode.D) ) actionsOut[0] = 1f;
        if( Input.GetKey(KeyCode.A) ) actionsOut[0] = -1f;
        
        //throttle
        actionsOut[1] = 0;
        if( Input.GetKey(KeyCode.W) ) actionsOut[1] = 1f;
        if( Input.GetKey(KeyCode.S) ) actionsOut[1] = -1f;

    }

	private float SmoothSteering(float steerInput) {
        steerInput *= VPcontrol.steering.maxSteerAngle;
		float steer = CurrentSteerDirection * VPcontrol.steering.maxSteerAngle;
        float steerStepsPerSec = (1 / Time.fixedDeltaTime);
        float steerDegPerStep = (SteerSpeedDegPerSec / steerStepsPerSec);
        float steerError = Mathf.Abs(steer - steerInput);
        
        
        //stay within the allowed range. P control?
        if(steer < steerInput && steer + steerDegPerStep < steerInput) steer += steerDegPerStep;
        else if(steer < steerInput && steer + steerDegPerStep > steerInput) steer = steerInput;
        
        else if(steer > steerInput && steer - steerDegPerStep > steerInput) steer -= steerDegPerStep;
        else if(steer > steerInput && steer - steerDegPerStep < steerInput) steer = steerInput;


        CurrentSteerDirection = steer / VPcontrol.steering.maxSteerAngle;
		return CurrentSteerDirection;
	}

}
