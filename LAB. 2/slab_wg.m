%waveguide with 3 layer structure
%This script calculates the analytic values of effective indexes and
%compares them to simulation values

%By default, this script analyzes the first 2 TE modes and 1st 2 TM modes.
%This can be changed in the figure section

%The analytic expressions are found in eq 13.2-4 and 13.2-5 on p499 of
%Optical Electronics in Modern Communication by Yariv

function [nTE,nTM]=slab_wg

lam = 1.55e-6;
t = 5e-6;       %thickness of core layer
n1 = 1;         %above core (air)
n2 = 1.44;      %core
n3 = 1.33;      %substrate  
k0 = 2*pi/lam;

b0 = linspace( max([n1 n3])*k0, n2*k0, 1000); %k0*n3 < b < k0*n2
b0 = b0(1:end-1);
te0=TE_eq(b0,k0,n1,n2,n3,t);
tm0=TM_eq(b0,k0,n1,n2,n3,t);

%TE
intervals=(te0>=0)-(te0<0);
izeros=find(diff(intervals)<0);
X0=[b0(izeros); b0(izeros+1)]';

[nzeros,scrap]=size(X0);

for i=1:nzeros
    nTE(i)=fzero(@(x) TE_eq(x,k0,n1,n2,n3,t),X0(i,:))/k0;
end
nTE=nTE(end:-1:1);

%TM
intervals=(tm0>=0)-(tm0<0);
izeros=find(diff(intervals)<0);
X0=[b0(izeros); b0(izeros+1)]';

[nzeros,scrap]=size(X0);

for i=1:nzeros
    nTM(i)=fzero(@(x) TM_eq(x,k0,n1,n2,n3,t),X0(i,:))/k0;
end
nTM=nTM(end:-1:1);

function te0=TE_eq(b0,k0,n1,n2,n3,t)

h0 = sqrt( (n2*k0)^2 - b0.^2 );
q0 = sqrt( b0.^2 - (n1*k0)^2 );
p0 = sqrt( b0.^2 - (n3*k0)^2 );

%the objective is to find zeroes of te0 and tm0
te0 = tan( h0*t ) - (p0+q0)./h0./(1-p0.*q0./h0.^2);

function tm0=TM_eq(b0,k0,n1,n2,n3,t)

h0 = sqrt( (n2*k0)^2 - b0.^2 );
q0 = sqrt( b0.^2 - (n1*k0)^2 );
p0 = sqrt( b0.^2 - (n3*k0)^2 );

pbar0 = (n2/n3)^2*p0;
qbar0 = (n2/n1)^2*q0;
tm0 = tan( h0*t ) - h0.*(pbar0+qbar0)./(h0.^2-pbar0.*qbar0);