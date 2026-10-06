#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
static constexpr int MAXN=500, MAXM=50;
struct Instance{int n=0,m=0; int p[MAXM][MAXN]{};};
Instance load_matrix(const string& path,int n,int m){
  Instance I; I.n=n; I.m=m; ifstream f(path); if(!f) throw runtime_error("open matrix");
  string line; int j=0; while(getline(f,line) && j<n){ stringstream ss(line); string tok; int mm=0; while(getline(ss,tok,',') && mm<m){ I.p[mm][j]=stoi(tok); mm++; } if(mm!=m) throw runtime_error("bad row"); j++; }
  if(j!=n) throw runtime_error("bad n"); return I;
}
inline int cmaxp(const Instance&I,const int*q){
  if(I.m==20){
    int c0=0,c1=0,c2=0,c3=0,c4=0,c5=0,c6=0,c7=0,c8=0,c9=0,c10=0,c11=0,c12=0,c13=0,c14=0,c15=0,c16=0,c17=0,c18=0,c19=0;
    for(int z=0;z<I.n;z++){int job=q[z];
      c0 += I.p[0][job]; c1=max(c1,c0)+I.p[1][job]; c2=max(c2,c1)+I.p[2][job]; c3=max(c3,c2)+I.p[3][job]; c4=max(c4,c3)+I.p[4][job];
      c5=max(c5,c4)+I.p[5][job]; c6=max(c6,c5)+I.p[6][job]; c7=max(c7,c6)+I.p[7][job]; c8=max(c8,c7)+I.p[8][job]; c9=max(c9,c8)+I.p[9][job];
      c10=max(c10,c9)+I.p[10][job]; c11=max(c11,c10)+I.p[11][job]; c12=max(c12,c11)+I.p[12][job]; c13=max(c13,c12)+I.p[13][job]; c14=max(c14,c13)+I.p[14][job];
      c15=max(c15,c14)+I.p[15][job]; c16=max(c16,c15)+I.p[16][job]; c17=max(c17,c16)+I.p[17][job]; c18=max(c18,c17)+I.p[18][job]; c19=max(c19,c18)+I.p[19][job];
    } return c19;
  }
  if(I.m==10){
    int c0=0,c1=0,c2=0,c3=0,c4=0,c5=0,c6=0,c7=0,c8=0,c9=0;
    for(int z=0;z<I.n;z++){int job=q[z];
      c0 += I.p[0][job]; c1=max(c1,c0)+I.p[1][job]; c2=max(c2,c1)+I.p[2][job]; c3=max(c3,c2)+I.p[3][job]; c4=max(c4,c3)+I.p[4][job];
      c5=max(c5,c4)+I.p[5][job]; c6=max(c6,c5)+I.p[6][job]; c7=max(c7,c6)+I.p[7][job]; c8=max(c8,c7)+I.p[8][job]; c9=max(c9,c8)+I.p[9][job];
    } return c9;
  }
  int c[MAXM]={0}; for(int z=0;z<I.n;z++){int job=q[z]; c[0]+=I.p[0][job]; for(int mm=1;mm<I.m;mm++) c[mm]=max(c[mm],c[mm-1])+I.p[mm][job];} return c[I.m-1];
}
struct Run{int best; double sec;};
Run ga(const Instance&I,int Ps,double pc,double pm,uint64_t seed,int G){
 mt19937_64 rng(seed); uniform_real_distribution<double> U(0.0,1.0); auto ri=[&](int a,int b){uniform_int_distribution<int>d(a,b);return d(rng);};
 const int n=I.n,k=n/2; vector<int> pop(Ps*n), nxt(Ps*n),fit(Ps),nfit(Ps); int pool[MAXN],c1[MAXN],c2[MAXN]; unsigned char mask[MAXN],u1[MAXN],u2[MAXN];
 for(int z=0;z<Ps;z++){int* q=&pop[z*n];for(int i=0;i<n;i++)q[i]=i;for(int i=n-1;i>0;i--){int j=ri(0,i);swap(q[i],q[j]);}fit[z]=cmaxp(I,q);} int gb=*min_element(fit.begin(),fit.end());
 auto tour=[&](){int a=ri(0,Ps-1),b=ri(0,Ps-1);while(b==a)b=ri(0,Ps-1);return fit[a]<=fit[b]?a:b;};
 auto mut=[&](int*q){int from=ri(0,n-1),to=ri(0,n-1);while(to==from)to=ri(0,n-1);int v=q[from];if(from<to){for(int i=from;i<to;i++)q[i]=q[i+1];q[to]=v;}else{for(int i=from;i>to;i--)q[i]=q[i-1];q[to]=v;}};
 auto cross=[&](const int*a,const int*b,int*x,int*y){for(int i=0;i<n;i++)pool[i]=i;for(int t=0;t<k;t++){int r=ri(t,n-1);swap(pool[t],pool[r]);}memset(mask,0,sizeof(mask));memset(u1,0,sizeof(u1));memset(u2,0,sizeof(u2));for(int i=0;i<n;i++){x[i]=-1;y[i]=-1;}for(int t=0;t<k;t++){int pos=pool[t];mask[pos]=1;x[pos]=a[pos];u1[a[pos]]=1;y[pos]=b[pos];u2[b[pos]]=1;}int ib=0,ia=0;for(int pos=0;pos<n;pos++)if(!mask[pos]){while(u1[b[ib]])++ib;x[pos]=b[ib++];while(u2[a[ia]])++ia;y[pos]=a[ia++];}};
 auto t0=chrono::steady_clock::now();
 for(int g=0;g<G;g++){
   int e=min_element(fit.begin(),fit.end())-fit.begin(); memcpy(&nxt[0],&pop[e*n],n*sizeof(int)); nfit[0]=fit[e]; int nz=1;
   while(nz<Ps){int ia=tour(),ib=tour();const int*a=&pop[ia*n],*b=&pop[ib*n];memcpy(c1,a,n*sizeof(int));memcpy(c2,b,n*sizeof(int));if(U(rng)<pc)cross(a,b,c1,c2);if(U(rng)<pm)mut(c1);if(U(rng)<pm)mut(c2);int f1=cmaxp(I,c1);memcpy(&nxt[nz*n],c1,n*sizeof(int));nfit[nz]=f1;gb=min(gb,f1);nz++;if(nz<Ps){int f2=cmaxp(I,c2);memcpy(&nxt[nz*n],c2,n*sizeof(int));nfit[nz]=f2;gb=min(gb,f2);nz++;}}
   pop.swap(nxt);fit.swap(nfit);
 }
 return {gb,chrono::duration<double>(chrono::steady_clock::now()-t0).count()};
}
int main(int ac,char**av){
 if(ac!=10){cerr<<"usage: PROGRAM matrix.csv n m G pop_mult pc pm seed output.csv\n";return 2;}
 string matrix=av[1], out=av[9]; int n=stoi(av[2]),m=stoi(av[3]),G=stoi(av[4]),mult=stoi(av[5]); double pc=stod(av[6]),pm=stod(av[7]); uint64_t seed=stoull(av[8]);
 Instance I=load_matrix(matrix,n,m); int Ps=mult*n; auto r=ga(I,Ps,pc,pm,seed,G);
 ofstream o(out); o<<"pop_mult,Ps,pc,pm,seed,G,best_cmax,run_sec\n"<<setprecision(12)<<mult<<','<<Ps<<','<<pc<<','<<pm<<','<<seed<<','<<G<<','<<r.best<<','<<r.sec<<"\n";
}
