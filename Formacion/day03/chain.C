#include <TChain.h>
#include <ROOT/RDataFrame.hxx>
#include <iostream>
#include <stdexcept>
void chain() {
    TChain tree("particles");
    if(tree.Add("data/day03_0.root")!=1 || tree.Add("data/day03_1.root")!=1)
        throw std::runtime_error("Ejecuta primero day03.numpy_root");
    ROOT::RDataFrame df(tree);
    std::cout << *df.Count() << " entradas; media " << *df.Mean("energy") << std::endl;
}
