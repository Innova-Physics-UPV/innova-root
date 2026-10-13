#include <ROOT/RDataFrame.hxx>
#include <iostream>
void analyze(const char* path="data/rftrack_amplitude_scan.root") {
    ROOT::RDataFrame df("simulations", path);
    std::cout << "Simulaciones: " << *df.Count() << std::endl;
    auto selected = df.Filter("A >= 0.10");
    std::cout << "Seleccionadas: " << *selected.Count() << std::endl;
    if(*selected.Count()>0)
        std::cout << "Media MeV: " << *selected.Mean("mean_kinetic_energy_MeV") << std::endl;
}
