using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using VehiclePhysics;

public class DriftAgentSimple: Agent
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

    	
	public float TireFrictionRandomMin = 0.7f;
	public float TireFrictionRandomMax = 1.1f;

    private PID_rpm_controller rpm_pid;

    float tmp=0f;



    void Awake()
    {
        //cache all later requiered components
        VPcontrol = GetComponent<VehiclePhysics.VPVehicleController>();
        VPinput = GetComponent<VehiclePhysics.VPStandardInput>();
        VPbase = GetComponent<VehiclePhysics.VehicleBase>();
        rb = GetComponent<Rigidbody>();
        imu = GetComponent<MeasurementUnit>();
        rpm_pid = gameObject.AddComponent<PID_rpm_controller>();
    }

    public override void OnEpisodeBegin()
    {


        //reset the agent
        this.transform.position = Vector3.zero + Vector3.up;


        rb.angularVelocity = Vector3.zero;
        rb.velocity = Vector3.zero;
        rb.ResetInertiaTensor();//does this do anything?
        

        VehiclePhysics.VPResetVehicle.ResetVehicle(VPbase, 0f);
        VPcontrol.data.Set(Channel.Input, InputData.ManualGear, 1);

        //randomizeTireFriction();
    }

    public override void CollectObservations(VectorSensor sensor)
    {

        Vector3 localVel = imu.LocalVelocity;
        Vector2 localVelXZ = new Vector2(localVel.x, localVel.z);
        sensor.AddObservation(localVelXZ / 300f);

        sensor.AddObservation(-rb.angularVelocity.y / 10f);

        sensor.AddObservation(Mathf.Abs(imu.SideSlip) / 180f);

        //sensor.AddObservation(VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / (1000.0f * VPcontrol.engine.maxRpm ));

        //sensor.AddObservation(CurrentSteerDirection);
        //sensor.AddObservation(traj.getDistOfCarToPath(transform) / MaxDistFromPath);
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
        //VPinput.externalThrottle += vectorAction[1] * 0.05f;
        VPinput.externalThrottle = 0.7f;
        //VPinput.externalThrottle += rpm_pid.Update_PID(vectorAction[1], VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / (1000.0f * VPcontrol.engine.maxRpm ));//Mathf.Clamp(VPinput.externalThrottle, 0f, 1f);
        //GraphDbg.Log((VPcontrol.data.Get(Channel.Vehicle, VehicleData.EngineRpm) / (1000.0f * VPcontrol.engine.maxRpm)));
        //if (VPinput.externalThrottle <= 0.1){
            //VPinput.externalHandbrake = 1;
        //}else{
            //VPinput.externalHandbrake = 0f;
        //}


        if (this.transform.position.magnitude > 100f) //|| Mathf.Abs(imu.SideSlip) > 110f)
        {
            //print("too far from path, resetting..." + traj.getDistOfCarToPath(this.transform));
            SetReward(-0.1f);
            EndEpisode();
        }


        float rew = (1f / (1f + Mathf.Pow(Mathf.Abs((Mathf.Abs(imu.SideSlip) - 30f)/10f),(2*1f)))) * 0.01f;
        if(Mathf.Sign(imu.LocalVelocity.x) == VPinput.externalSteer){
            rew = (1f / (1f + Mathf.Pow(Mathf.Abs((Mathf.Abs(imu.SideSlip) - 30f)/10f),(2*1f))));
        }
        
        SetReward(rew);
        
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
        //actionsOut[1] = 0;
        //if( Input.GetKey(KeyCode.W) ) actionsOut[1] = 1f;
        //if( Input.GetKey(KeyCode.S) ) actionsOut[1] = -1f;

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
