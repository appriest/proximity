double single(double *x, double *par){
	double const pi = 4*atan(1.);
	return pow(sin(pi*par[0]*x[0])/(pi*par[0]*x[0]),2);
}

double nslit0(double *x, double *par){
	double const pi = 4*atan(1.);
	return pow(sin(pi*par[1]*x[0])/sin(pi*x[0]),2);
}

double nslit(double *x, double *par){
	return single(x,par) * nslit0(x,par);
}

void slits(){
	float r,ns;

	cout << "slit width / g ? ";
	scanf("%f",&r);
	cout << "# of slits? ";
	scanf("%f",&ns);
	cout << "interference pattern for " << ns << " slits, width/distance: " << r << endl;

	TF1 *Fnslit = new TF1("Fnslit",nslit,-5.001,5.,2);
	Fnslit->SetNpx(500);

	Fnslit->SetParameter(0,r);
	Fnslit->SetParameter(1,ns);

	Fnslit->Draw();
}
