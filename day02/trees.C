// Reconstrucción didáctica de PDF §6.1-6.4; valores de ejemplo nuevos.
#include <TFile.h>
#include <TTree.h>
#include <stdexcept>
#include <iostream>
void trees(const char* path="data/day02.root") {
    {
        TFile f(path, "RECREATE");
        if (f.IsZombie()) throw std::runtime_error("No se puede crear TFile");
        TTree tree("particles", "Ejemplo de lectura y escritura");
        double x=0, y=0, energy=0;
        tree.Branch("x", &x, "x/D");
        tree.Branch("y", &y, "y/D");
        tree.Branch("energy", &energy, "energy/D");
        for(int i=0; i<5; ++i) {x=i; y=-i; energy=10+i; tree.Fill();}
        tree.Write();
    }
    TFile f(path, "READ");
    if(f.IsZombie()) throw std::runtime_error("No se puede abrir TFile");
    auto* tree = f.Get<TTree>("particles");
    if(!tree) throw std::runtime_error("Falta particles");
    double x=0, y=0, energy=0;
    if(tree->SetBranchAddress("x", &x)<0 || tree->SetBranchAddress("y", &y)<0 ||
       tree->SetBranchAddress("energy", &energy)<0) throw std::runtime_error("Ramas incompatibles");
    for(Long64_t i=0; i<tree->GetEntries(); ++i) {
        if(tree->GetEntry(i)<=0) throw std::runtime_error("Error de lectura");
        std::cout << i << " " << x << " " << y << " " << energy << std::endl;
    }
    tree->ResetBranchAddresses();
}
