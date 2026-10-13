// Reconstrucción didáctica de PDF §6.1-6.4; valores de ejemplo nuevos.
#include <TFile.h>
#include <TTree.h>
#include <stdexcept>
#include <iostream>
void trees(const char* path="data/day02.root") {
    {
        // TFile es el archivo. RECREATE reemplaza un archivo existente.
        TFile f(path, "RECREATE");
        if (f.IsZombie()) throw std::runtime_error("No se puede crear TFile");
        // TTree es una tabla; Branch conecta cada columna con una variable.
        TTree tree("particles", "Ejemplo de lectura y escritura");
        double x=0, y=0, energy=0;
        tree.Branch("x", &x, "x/D");
        tree.Branch("y", &y, "y/D");
        tree.Branch("energy", &energy, "energy/D");
        // Fill copia los valores actuales en una nueva fila.
        for(int i=0; i<5; ++i) {
            x = i;
            y = -i;
            energy = 10 + i;
            tree.Fill();
        }
        tree.Write();
    }
    // Al salir del bloque anterior, el archivo de escritura se cierra.
    TFile f(path, "READ");
    if(f.IsZombie()) throw std::runtime_error("No se puede abrir TFile");
    auto* tree = f.Get<TTree>("particles");
    if(!tree) throw std::runtime_error("Falta particles");
    // SetBranchAddress indica dónde cargar los valores al leer una entrada.
    double x=0, y=0, energy=0;
    if(tree->SetBranchAddress("x", &x)<0 || tree->SetBranchAddress("y", &y)<0 ||
       tree->SetBranchAddress("energy", &energy)<0) throw std::runtime_error("Ramas incompatibles");
    // GetEntry carga la fila i en x, y y energy.
    for(Long64_t i=0; i<tree->GetEntries(); ++i) {
        if(tree->GetEntry(i)<=0) throw std::runtime_error("Error de lectura");
        std::cout << i << " " << x << " " << y << " " << energy << std::endl;
    }
    tree->ResetBranchAddresses();
}
