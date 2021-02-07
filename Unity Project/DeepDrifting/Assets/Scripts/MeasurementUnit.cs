using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
//using VehiclePhysics;

public class MeasurementUnit : MonoBehaviour
{
    //[SerializeField]
    //private Text slipAngleDisplay;

    private Rigidbody rBody;

    //[DebugGUIGraph(min: -100, max: 100, r: 0, g: 1, b: 0, autoScale: false)]
    public float SideSlip;

    public Vector3 LocalVelocity;



    // Start is called before the first frame update
    void Awake()
    {
        rBody = GetComponent<Rigidbody>();
    }

    // Update is called once per frame
    void Update()
    {
        LocalVelocity = calculateLocalVelocity();
        SideSlip = calculateSideSlip();
        
        //slipAngleDisplay.text = Mathf.Round(SideSlip).ToString() + "°";// Mathf.Round(100*rew).ToString() + "°";
    }

    private float calculateSideSlip(){
        Vector2 vel = new Vector2(LocalVelocity.x, LocalVelocity.z);
        Vector2 velNormed = vel.normalized;

        float beta = (Mathf.Rad2Deg * Mathf.Atan2(velNormed.x , velNormed.y)); //x,y not y,x because car's forward is 3d Z and in 2d Y axis
        if(Mathf.Abs(vel.x) <= 0.001f || Mathf.Abs(vel.y) <= 0.001f ) beta = 0;

        //avoid +-180° fluctiations at very low speeds
        if(vel.magnitude <= 0.18f) beta = 0f; //0.2f is first gear idle speed

        //sideslip angle ß
        return beta;
    }


    private Vector3 calculateLocalVelocity(){
        Vector3 localVelocity = rBody.transform.InverseTransformDirection(rBody.velocity);
        //Vector3 velNormed = Vector3.Normalize(localVelocity);
        return localVelocity;
    }

    
    void OnDrawGizmosSelected()
    {
        //Debug.DrawRay(car.transform.position, Vector3.forward, Color.green);

        //vector facing in direction of heading (forward)
        Gizmos.DrawLine(transform.position, transform.position + transform.forward * 3);

        //vector facing in direction of travel
        Gizmos.DrawLine(transform.position, rBody.velocity + transform.position);

        
    }
}
