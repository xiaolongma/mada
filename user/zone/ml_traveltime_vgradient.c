/*
 *  ml_traveltime_vgradient.c
 *  
 *
 *  Created by Yanadet Sripanich on 10/31/12.
 *  Copyright 2012 __MyCompanyName__. All rights reserved.
 *
 */

#include "ml_traveltime_vgradient.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "general_traveltime.h"
/*^*/

float v(twod y_k, twod x_ref)
{
	
	float v;
	
	v = x_ref.v + y_k.gx*(y_k.x-x_ref.x)+y_k.gz*(y_k.z-x_ref.z);
	y_k.v = v;
	
	return y_k.v;
} 

/*calculate z outsideeeeee !!!*/

float T_k(twod y_k,twod y_k1)
/*<Traveltime>*/
{
	float t_k;
	
	t_k = (1/hypotf(y_k.gx,y_k.gz))*log((1+(pow(hypotf(y_k.gx,y_k.gz),2)*pow((y_k1.x-y_k.x),2))/(2*y_k.v*y_k1.v))+sqrt(pow(1+(pow(hypotf(y_k.gx,y_k.gz),2)*pow((y_k1.x-y_k.x),2))/(2*y_k.v*y_k1.v),2)-1));
	
	return t_k;
	
}

float T_k_k(twod y_k, twod y_k1)
/*<Derivative of T with respect to x_k>*/
{
	float t_k_k,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k = (sqrt(2)*g0*(y_k.x-y_k1.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));
	
	return t_k_k;
	
}
	

float T_k_k1(twod y_k, twod y_k1)
/*<Derivative of T with respect to x_k1>*/
{
	float t_k_k1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k1 = (sqrt(2)*g0*(y_k1.x-y_k.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));
	
	return t_k_k1;
	
}

float T_k_k_k(twod y_k, twod y_k1)  
/*<Second derivative of T with respect to x_k>*/
{
	float t_k_k_k,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k_k = ((-1)*sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) - (sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));	
	
	return t_k_k_k;
	
}

float T_k_k1_k1(twod y_k, twod y_k1) 
/*<Second derivative of T with respect to x_k1>*/
{
	float t_k_k1_k1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k1_k1 = ((-1)*sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) - (sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));		
	
	return t_k_k1_k1;
	
}


float T_k_k_k1(twod y_k, twod y_k1) 
/*<Second derivative of T with respect to x_k and x_k1>*/
{
	float t_k_k_k1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k_k1 = (sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) - (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) + (sqrt(2)*pow(g0,3)*pow(y_k.x-y_k1.x,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));
	
	return t_k_k_k1;
	
}


float T_k_zk(twod y_k, twod y_k1) 
/*<Derivative of T with respect to z_k>*/
{
	float t_k_zk,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_zk = (sqrt(2)*g0*(y_k.z-y_k1.z))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));
	
	return t_k_zk;
	
}

float T_k_zk1(twod y_k, twod y_k1) 
/*<Derivative of T with respect to z_k1>*/
{
	float t_k_zk1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_zk1 = (sqrt(2)*g0*(y_k1.z-y_k.z))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));
	
	return t_k_zk1;
	
}

float T_k_zk_zk(twod y_k, twod y_k1)  
/*<Second Derivative of T with respect to z_k>*/
{
	float t_k_zk_zk,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_zk_zk = ((-1)*sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) - (sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));	
	
	return t_k_zk_zk;
	
}

float T_k_zk1_zk1(twod y_k, twod y_k1)  
/*<Second Derivative of T with respect to z_k1>*/
{
	float t_k_zk1_zk1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_zk1_zk1 = ((-1)*sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) - (sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));	
	
	return t_k_zk1_zk1;
	
}

float T_k_zk_zk1(twod y_k, twod y_k1)  
/*<Second Derivative of T with respect to z_k and z_k1>*/
{
	float t_k_zk_zk1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_zk_zk1 = (sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) - (sqrt(2)*g0)/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*y_k.v*y_k1.v*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))) + (sqrt(2)*pow(g0,3)*pow(y_k.z-y_k1.z,2))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));	
	
	return t_k_zk_zk1;
	
}


float T_k_k_zk(twod y_k, twod y_k1) 
/*<Second derivative of T with respect to x_k and z_k>*/
{
	float t_k_k_zk,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k_zk = (sqrt(2)*pow(g0,3)*(y_k1.z-y_k.z)*(y_k.x-y_k1.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*pow(g0,3)*(y_k1.z-y_k.z)*(y_k.x-y_k1.x))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));		
	
	return t_k_k_zk;
	
}

float T_k_k1_zk1(twod y_k, twod y_k1) 
/*<Second derivative of T with respect to x_k1 and z_k1>*/
{
	float t_k_k1_zk1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k1_zk1 = (sqrt(2)*pow(g0,3)*(y_k1.z-y_k.z)*(y_k.x-y_k1.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*pow(g0,3)*(y_k1.z-y_k.z)*(y_k.x-y_k1.x))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v)));		
	
	return t_k_k1_zk1;
	
}

float T_k_k_zk1(twod y_k, twod y_k1)  
/*<Second derivative of T with respect to x_k and z_k1>*/
{
	float t_k_k_zk1,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	
	t_k_k_zk1 = ((sqrt(2)*pow(g0,3)*(y_k.z-y_k1.z)*(y_k.x-y_k1.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*pow(g0,3)*(y_k.z-y_k1.z)*(y_k.x-y_k1.x))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))));	
	
	return t_k_k_zk1;
	
}

float T_k_k1_zk(twod y_k, twod y_k1)  
/*<Second derivative of T with respect to x_k1 and z_k>*/
{
	float t_k_k1_zk,g0;
	
	g0 = hypotf(y_k.gx,y_k.gz);
	
	t_k_k1_zk = ((sqrt(2)*pow(g0,3)*(y_k.z-y_k1.z)*(y_k.x-y_k1.x))/(sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v))+2*pow(y_k.v,2)*pow(y_k1.v,2)*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v),3/2)) + (sqrt(2)*pow(g0,3)*(y_k.z-y_k1.z)*(y_k.x-y_k1.x))/(2*pow(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(2*y_k.v*y_k1.v)+2,3/2)*pow(y_k.v,2)*pow(y_k1.v,2)*sqrt(pow(g0,2)*(pow(y_k.z-y_k1.z,2)+pow(y_k.x-y_k1.x,2))/(y_k.v*y_k1.v))));	
	
	return t_k_k1_zk;
	
}
