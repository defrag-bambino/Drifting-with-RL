using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PID_rpm_controller : MonoBehaviour
{

    //https://github.com/Atknssl/Unity-PID-Examples/blob/master/Assets/Scripts/PID.cs


	public float pFactor=0.01f, iFactor=0.0004f, dFactor;

	private float _integral;
	private float _lastError;

	public float tar;
	// public PID(float pFactor, float iFactor, float dFactor)
	// {
	// 	this.pFactor = pFactor;
	// 	this.iFactor = iFactor;
	// 	this.dFactor = dFactor;
	// }
	public float Update_PID(float target, float current)
	{
        float deltatime = Time.fixedDeltaTime;
		LimitIntegral(10f);

		float error = target - current;
		_integral += error * deltatime;
		float derivative = (error - _lastError) / deltatime;
		_lastError = error;
		return error * pFactor + _integral * iFactor + derivative * dFactor;
	}
	public void LimitIntegral(float value)
	{
		if (_integral >= value)
		{
			_integral = value;
		}
		if (_integral <= -value)
		{
			_integral = -value;
		}
	}
}
