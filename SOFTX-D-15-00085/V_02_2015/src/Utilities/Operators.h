/*
 * Operators.h (unified host/device)
 *
 * Merged from Utilities/Host/Operators.h and Utilities/Device/Opertators.cuh
 * Original author: Nicolin Govender, Jun 5, 2014
 */

#ifndef UNIFIED_OPERATORS_H_
#define UNIFIED_OPERATORS_H_

#include "Functions.h"

#ifdef __CUDACC__
#define HD __host__ __device__
#else
#define HD
#endif

/*---------------------------------------------------------------------------*/
/* float3 operators (host and device)                                        */
/*---------------------------------------------------------------------------*/

inline HD float3 operator+(float3 a, float3 b)
{
    return make_float3(a.x + b.x, a.y + b.y, a.z + b.z);
}

inline HD float3 operator-(float3 a, float3 b)
{
    return make_float3(a.x - b.x, a.y - b.y, a.z - b.z);
}

inline HD float3 operator*(float3 a, float3 b)
{
    return make_float3(a.x * b.x, a.y * b.y, a.z * b.z);
}

inline HD float3 operator*(float b, float3 a)
{
    return make_float3(b * a.x, b * a.y, b * a.z);
}

inline HD float3 operator*(float3 a, float b)
{
    return make_float3(a.x * b, a.y * b, a.z * b);
}

inline HD float3 operator/(float3 a, float3 b)
{
    return make_float3(a.x / b.x, a.y / b.y, a.z / b.z);
}

inline HD float3 operator/(float3 a, float b)
{
    return make_float3(a.x / b, a.y / b, a.z / b);
}

inline HD float3 operator/(float b, float3 a)
{
    return make_float3(b / a.x, b / a.y, b / a.z);
}

inline HD void operator+=(float3 &a, float3 b)
{
    a.x += b.x;
    a.y += b.y;
    a.z += b.z;
}

inline HD void operator+=(float3 &a, float b)
{
    a.x += b;
    a.y += b;
    a.z += b;
}

inline HD void operator/=(float3 &a, float b)
{
    a.x /= b;
    a.y /= b;
    a.z /= b;
}

/*---------------------------------------------------------------------------*/
/* Device-only extended operators                                            */
/*---------------------------------------------------------------------------*/
#ifdef __CUDACC__

////////////////////////////////////////////////////////////////////////////////
// negate
////////////////////////////////////////////////////////////////////////////////

inline __device__ float2 operator-(float2 &a)
{
    return make_float2(-a.x, -a.y);
}
inline __device__ int2 operator-(int2 &a)
{
    return make_int2(-a.x, -a.y);
}
inline __device__ float3 operator-(float3 &a)
{
    return make_float3(-a.x, -a.y, -a.z);
}
inline __device__ int3 operator-(int3 &a)
{
    return make_int3(-a.x, -a.y, -a.z);
}
inline __device__ float4 operator-(float4 &a)
{
    return make_float4(-a.x, -a.y, -a.z, -a.w);
}
inline __device__ int4 operator-(int4 &a)
{
    return make_int4(-a.x, -a.y, -a.z, -a.w);
}

////////////////////////////////////////////////////////////////////////////////
// float3 device-only extras
////////////////////////////////////////////////////////////////////////////////

inline __device__ void operator-=(float3 &a, float3 b)
{
    a.x -= b.x; a.y -= b.y; a.z -= b.z;
}
inline __device__ float3 operator-(float3 a, float b)
{
    return make_float3(a.x - b, a.y - b, a.z - b);
}
inline __device__ float3 operator-(float b, float3 a)
{
    return make_float3(b - a.x, b - a.y, b - a.z);
}
inline __device__ void operator-=(float3 &a, float b)
{
    a.x -= b; a.y -= b; a.z -= b;
}
inline __device__ float3 operator+(float3 a, float b)
{
    return make_float3(a.x + b, a.y + b, a.z + b);
}
inline __device__ float3 operator+(float b, float3 a)
{
    return make_float3(a.x + b, a.y + b, a.z + b);
}
inline __device__ void operator*=(float3 &a, float3 b)
{
    a.x *= b.x; a.y *= b.y; a.z *= b.z;
}
inline __device__ void operator*=(float3 &a, float b)
{
    a.x *= b; a.y *= b; a.z *= b;
}
inline __device__ void operator/=(float3 &a, float3 b)
{
    a.x /= b.x; a.y /= b.y; a.z /= b.z;
}

////////////////////////////////////////////////////////////////////////////////
// float2 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ float2 operator+(float2 a, float2 b) { return make_float2(a.x + b.x, a.y + b.y); }
inline __device__ void operator+=(float2 &a, float2 b) { a.x += b.x; a.y += b.y; }
inline __device__ float2 operator+(float2 a, float b) { return make_float2(a.x + b, a.y + b); }
inline __device__ float2 operator+(float b, float2 a) { return make_float2(a.x + b, a.y + b); }
inline __device__ void operator+=(float2 &a, float b) { a.x += b; a.y += b; }
inline __device__ float2 operator-(float2 a, float2 b) { return make_float2(a.x - b.x, a.y - b.y); }
inline __device__ void operator-=(float2 &a, float2 b) { a.x -= b.x; a.y -= b.y; }
inline __device__ float2 operator-(float2 a, float b) { return make_float2(a.x - b, a.y - b); }
inline __device__ float2 operator-(float b, float2 a) { return make_float2(b - a.x, b - a.y); }
inline __device__ void operator-=(float2 &a, float b) { a.x -= b; a.y -= b; }
inline __device__ float2 operator*(float2 a, float2 b) { return make_float2(a.x * b.x, a.y * b.y); }
inline __device__ void operator*=(float2 &a, float2 b) { a.x *= b.x; a.y *= b.y; }
inline __device__ float2 operator*(float2 a, float b) { return make_float2(a.x * b, a.y * b); }
inline __device__ float2 operator*(float b, float2 a) { return make_float2(b * a.x, b * a.y); }
inline __device__ void operator*=(float2 &a, float b) { a.x *= b; a.y *= b; }
inline __device__ float2 operator/(float2 a, float2 b) { return make_float2(a.x / b.x, a.y / b.y); }
inline __device__ void operator/=(float2 &a, float2 b) { a.x /= b.x; a.y /= b.y; }
inline __device__ float2 operator/(float2 a, float b) { return make_float2(a.x / b, a.y / b); }
inline __device__ void operator/=(float2 &a, float b) { a.x /= b; a.y /= b; }
inline __device__ float2 operator/(float b, float2 a) { return make_float2(b / a.x, b / a.y); }

////////////////////////////////////////////////////////////////////////////////
// int2 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ int2 operator+(int2 a, int2 b) { return make_int2(a.x + b.x, a.y + b.y); }
inline __device__ void operator+=(int2 &a, int2 b) { a.x += b.x; a.y += b.y; }
inline __device__ int2 operator+(int2 a, int b) { return make_int2(a.x + b, a.y + b); }
inline __device__ int2 operator+(int b, int2 a) { return make_int2(a.x + b, a.y + b); }
inline __device__ void operator+=(int2 &a, int b) { a.x += b; a.y += b; }
inline __device__ int2 operator-(int2 a, int2 b) { return make_int2(a.x - b.x, a.y - b.y); }
inline __device__ void operator-=(int2 &a, int2 b) { a.x -= b.x; a.y -= b.y; }
inline __device__ int2 operator-(int2 a, int b) { return make_int2(a.x - b, a.y - b); }
inline __device__ int2 operator-(int b, int2 a) { return make_int2(b - a.x, b - a.y); }
inline __device__ void operator-=(int2 &a, int b) { a.x -= b; a.y -= b; }
inline __device__ int2 operator*(int2 a, int2 b) { return make_int2(a.x * b.x, a.y * b.y); }
inline __device__ void operator*=(int2 &a, int2 b) { a.x *= b.x; a.y *= b.y; }
inline __device__ int2 operator*(int2 a, int b) { return make_int2(a.x * b, a.y * b); }
inline __device__ int2 operator*(int b, int2 a) { return make_int2(b * a.x, b * a.y); }
inline __device__ void operator*=(int2 &a, int b) { a.x *= b; a.y *= b; }

////////////////////////////////////////////////////////////////////////////////
// uint2 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ uint2 operator+(uint2 a, uint2 b) { return make_uint2(a.x + b.x, a.y + b.y); }
inline __device__ void operator+=(uint2 &a, uint2 b) { a.x += b.x; a.y += b.y; }
inline __device__ uint2 operator+(uint2 a, uint b) { return make_uint2(a.x + b, a.y + b); }
inline __device__ uint2 operator+(uint b, uint2 a) { return make_uint2(a.x + b, a.y + b); }
inline __device__ void operator+=(uint2 &a, uint b) { a.x += b; a.y += b; }
inline __device__ uint2 operator-(uint2 a, uint2 b) { return make_uint2(a.x - b.x, a.y - b.y); }
inline __device__ void operator-=(uint2 &a, uint2 b) { a.x -= b.x; a.y -= b.y; }
inline __device__ uint2 operator-(uint2 a, uint b) { return make_uint2(a.x - b, a.y - b); }
inline __device__ uint2 operator-(uint b, uint2 a) { return make_uint2(b - a.x, b - a.y); }
inline __device__ void operator-=(uint2 &a, uint b) { a.x -= b; a.y -= b; }
inline __device__ uint2 operator*(uint2 a, uint2 b) { return make_uint2(a.x * b.x, a.y * b.y); }
inline __device__ void operator*=(uint2 &a, uint2 b) { a.x *= b.x; a.y *= b.y; }
inline __device__ uint2 operator*(uint2 a, uint b) { return make_uint2(a.x * b, a.y * b); }
inline __device__ uint2 operator*(uint b, uint2 a) { return make_uint2(b * a.x, b * a.y); }
inline __device__ void operator*=(uint2 &a, uint b) { a.x *= b; a.y *= b; }

////////////////////////////////////////////////////////////////////////////////
// int3 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ int3 operator+(int3 a, int3 b) { return make_int3(a.x + b.x, a.y + b.y, a.z + b.z); }
inline __device__ void operator+=(int3 &a, int3 b) { a.x += b.x; a.y += b.y; a.z += b.z; }
inline __device__ int3 operator+(int3 a, int b) { return make_int3(a.x + b, a.y + b, a.z + b); }
inline __device__ int3 operator+(int b, int3 a) { return make_int3(a.x + b, a.y + b, a.z + b); }
inline __device__ void operator+=(int3 &a, int b) { a.x += b; a.y += b; a.z += b; }
inline __device__ int3 operator-(int3 a, int3 b) { return make_int3(a.x - b.x, a.y - b.y, a.z - b.z); }
inline __device__ void operator-=(int3 &a, int3 b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; }
inline __device__ int3 operator-(int3 a, int b) { return make_int3(a.x - b, a.y - b, a.z - b); }
inline __device__ int3 operator-(int b, int3 a) { return make_int3(b - a.x, b - a.y, b - a.z); }
inline __device__ void operator-=(int3 &a, int b) { a.x -= b; a.y -= b; a.z -= b; }
inline __device__ int3 operator*(int3 a, int3 b) { return make_int3(a.x * b.x, a.y * b.y, a.z * b.z); }
inline __device__ void operator*=(int3 &a, int3 b) { a.x *= b.x; a.y *= b.y; a.z *= b.z; }
inline __device__ int3 operator*(int3 a, int b) { return make_int3(a.x * b, a.y * b, a.z * b); }
inline __device__ int3 operator*(int b, int3 a) { return make_int3(b * a.x, b * a.y, b * a.z); }
inline __device__ void operator*=(int3 &a, int b) { a.x *= b; a.y *= b; a.z *= b; }

////////////////////////////////////////////////////////////////////////////////
// uint3 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ uint3 operator+(uint3 a, uint3 b) { return make_uint3(a.x + b.x, a.y + b.y, a.z + b.z); }
inline __device__ void operator+=(uint3 &a, uint3 b) { a.x += b.x; a.y += b.y; a.z += b.z; }
inline __device__ uint3 operator+(uint3 a, uint b) { return make_uint3(a.x + b, a.y + b, a.z + b); }
inline __device__ uint3 operator+(uint b, uint3 a) { return make_uint3(a.x + b, a.y + b, a.z + b); }
inline __device__ void operator+=(uint3 &a, uint b) { a.x += b; a.y += b; a.z += b; }
inline __device__ uint3 operator-(uint3 a, uint3 b) { return make_uint3(a.x - b.x, a.y - b.y, a.z - b.z); }
inline __device__ void operator-=(uint3 &a, uint3 b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; }
inline __device__ uint3 operator-(uint3 a, uint b) { return make_uint3(a.x - b, a.y - b, a.z - b); }
inline __device__ uint3 operator-(uint b, uint3 a) { return make_uint3(b - a.x, b - a.y, b - a.z); }
inline __device__ void operator-=(uint3 &a, uint b) { a.x -= b; a.y -= b; a.z -= b; }
inline __device__ uint3 operator*(uint3 a, uint3 b) { return make_uint3(a.x * b.x, a.y * b.y, a.z * b.z); }
inline __device__ void operator*=(uint3 &a, uint3 b) { a.x *= b.x; a.y *= b.y; a.z *= b.z; }
inline __device__ uint3 operator*(uint3 a, uint b) { return make_uint3(a.x * b, a.y * b, a.z * b); }
inline __device__ uint3 operator*(uint b, uint3 a) { return make_uint3(b * a.x, b * a.y, b * a.z); }
inline __device__ void operator*=(uint3 &a, uint b) { a.x *= b; a.y *= b; a.z *= b; }

////////////////////////////////////////////////////////////////////////////////
// float4 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ float4 operator+(float4 a, float4 b) { return make_float4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w); }
inline __device__ void operator+=(float4 &a, float4 b) { a.x += b.x; a.y += b.y; a.z += b.z; a.w += b.w; }
inline __device__ float4 operator+(float4 a, float b) { return make_float4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ float4 operator+(float b, float4 a) { return make_float4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ void operator+=(float4 &a, float b) { a.x += b; a.y += b; a.z += b; a.w += b; }
inline __device__ float4 operator-(float4 a, float4 b) { return make_float4(a.x - b.x, a.y - b.y, a.z - b.z, a.w - b.w); }
inline __device__ void operator-=(float4 &a, float4 b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; a.w -= b.w; }
inline __device__ float4 operator-(float4 a, float b) { return make_float4(a.x - b, a.y - b, a.z - b, a.w - b); }
inline __device__ void operator-=(float4 &a, float b) { a.x -= b; a.y -= b; a.z -= b; a.w -= b; }
inline __device__ float4 operator*(float4 a, float4 b) { return make_float4(a.x * b.x, a.y * b.y, a.z * b.z, a.w * b.w); }
inline __device__ void operator*=(float4 &a, float4 b) { a.x *= b.x; a.y *= b.y; a.z *= b.z; a.w *= b.w; }
inline __device__ float4 operator*(float4 a, float b) { return make_float4(a.x * b, a.y * b, a.z * b, a.w * b); }
inline __device__ float4 operator*(float b, float4 a) { return make_float4(b * a.x, b * a.y, b * a.z, b * a.w); }
inline __device__ void operator*=(float4 &a, float b) { a.x *= b; a.y *= b; a.z *= b; a.w *= b; }
inline __device__ float4 operator/(float4 a, float4 b) { return make_float4(a.x / b.x, a.y / b.y, a.z / b.z, a.w / b.w); }
inline __device__ void operator/=(float4 &a, float4 b) { a.x /= b.x; a.y /= b.y; a.z /= b.z; a.w /= b.w; }
inline __device__ float4 operator/(float4 a, float b) { return make_float4(a.x / b, a.y / b, a.z / b, a.w / b); }
inline __device__ void operator/=(float4 &a, float b) { a.x /= b; a.y /= b; a.z /= b; a.w /= b; }
inline __device__ float4 operator/(float b, float4 a) { return make_float4(b / a.x, b / a.y, b / a.z, b / a.w); }

////////////////////////////////////////////////////////////////////////////////
// int4 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ int4 operator+(int4 a, int4 b) { return make_int4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w); }
inline __device__ void operator+=(int4 &a, int4 b) { a.x += b.x; a.y += b.y; a.z += b.z; a.w += b.w; }
inline __device__ int4 operator+(int4 a, int b) { return make_int4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ int4 operator+(int b, int4 a) { return make_int4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ void operator+=(int4 &a, int b) { a.x += b; a.y += b; a.z += b; a.w += b; }
inline __device__ int4 operator-(int4 a, int4 b) { return make_int4(a.x - b.x, a.y - b.y, a.z - b.z, a.w - b.w); }
inline __device__ void operator-=(int4 &a, int4 b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; a.w -= b.w; }
inline __device__ int4 operator-(int4 a, int b) { return make_int4(a.x - b, a.y - b, a.z - b, a.w - b); }
inline __device__ int4 operator-(int b, int4 a) { return make_int4(b - a.x, b - a.y, b - a.z, b - a.w); }
inline __device__ void operator-=(int4 &a, int b) { a.x -= b; a.y -= b; a.z -= b; a.w -= b; }
inline __device__ int4 operator*(int4 a, int4 b) { return make_int4(a.x * b.x, a.y * b.y, a.z * b.z, a.w * b.w); }
inline __device__ void operator*=(int4 &a, int4 b) { a.x *= b.x; a.y *= b.y; a.z *= b.z; a.w *= b.w; }
inline __device__ int4 operator*(int4 a, int b) { return make_int4(a.x * b, a.y * b, a.z * b, a.w * b); }
inline __device__ int4 operator*(int b, int4 a) { return make_int4(b * a.x, b * a.y, b * a.z, b * a.w); }
inline __device__ void operator*=(int4 &a, int b) { a.x *= b; a.y *= b; a.z *= b; a.w *= b; }

////////////////////////////////////////////////////////////////////////////////
// uint4 operators
////////////////////////////////////////////////////////////////////////////////

inline __device__ uint4 operator+(uint4 a, uint4 b) { return make_uint4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w); }
inline __device__ void operator+=(uint4 &a, uint4 b) { a.x += b.x; a.y += b.y; a.z += b.z; a.w += b.w; }
inline __device__ uint4 operator+(uint4 a, uint b) { return make_uint4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ uint4 operator+(uint b, uint4 a) { return make_uint4(a.x + b, a.y + b, a.z + b, a.w + b); }
inline __device__ void operator+=(uint4 &a, uint b) { a.x += b; a.y += b; a.z += b; a.w += b; }
inline __device__ uint4 operator-(uint4 a, uint4 b) { return make_uint4(a.x - b.x, a.y - b.y, a.z - b.z, a.w - b.w); }
inline __device__ void operator-=(uint4 &a, uint4 b) { a.x -= b.x; a.y -= b.y; a.z -= b.z; a.w -= b.w; }
inline __device__ uint4 operator-(uint4 a, uint b) { return make_uint4(a.x - b, a.y - b, a.z - b, a.w - b); }
inline __device__ uint4 operator-(uint b, uint4 a) { return make_uint4(b - a.x, b - a.y, b - a.z, b - a.w); }
inline __device__ void operator-=(uint4 &a, uint b) { a.x -= b; a.y -= b; a.z -= b; a.w -= b; }
inline __device__ uint4 operator*(uint4 a, uint4 b) { return make_uint4(a.x * b.x, a.y * b.y, a.z * b.z, a.w * b.w); }
inline __device__ void operator*=(uint4 &a, uint4 b) { a.x *= b.x; a.y *= b.y; a.z *= b.z; a.w *= b.w; }
inline __device__ uint4 operator*(uint4 a, uint b) { return make_uint4(a.x * b, a.y * b, a.z * b, a.w * b); }
inline __device__ uint4 operator*(uint b, uint4 a) { return make_uint4(b * a.x, b * a.y, b * a.z, b * a.w); }
inline __device__ void operator*=(uint4 &a, uint b) { a.x *= b; a.y *= b; a.z *= b; a.w *= b; }

////////////////////////////////////////////////////////////////////////////////
// Quaternion operators (device only - host versions are in Quart.h)
////////////////////////////////////////////////////////////////////////////////

inline __device__ Quaterion operator+(Quaterion Q1, Quaterion Q2)
{
    Quaterion q;
    q.w = Q1.w + Q2.w;
    q.x = Q1.x + Q2.x;
    q.y = Q1.y + Q2.y;
    q.z = Q1.z + Q2.z;
    return q;
}

inline __device__ Quaterion operator*(Quaterion q1, Quaterion q2)
{
    Quaterion q;
    q.x =  (q1.x * q2.w) + (q1.y * q2.z) - (q1.z * q2.y) + (q1.w * q2.x);
    q.y = -(q1.x * q2.z) + (q1.y * q2.w) + (q1.z * q2.x) + (q1.w * q2.y);
    q.z =  (q1.x * q2.y) - (q1.y * q2.x) + (q1.z * q2.w) + (q1.w * q2.z);
    q.w = -(q1.x * q2.x) - (q1.y * q2.y) - (q1.z * q2.z) + (q1.w * q2.w);
    return q;
}

inline __device__ float3 operator*(float3 v, float *M)
{
    float3 vec;
    vec.x = (v.x*M[0] + v.y*M[3] + v.z*M[6]);
    vec.y = (v.x*M[1] + v.y*M[4] + v.z*M[7]);
    vec.z = (v.x*M[2] + v.y*M[5] + v.z*M[8]);
    return vec;
}

#endif /* __CUDACC__ */

#undef HD

#endif /* UNIFIED_OPERATORS_H_ */
