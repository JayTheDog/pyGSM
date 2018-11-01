import options
from pes import * 

class Penalty_PES(PES):
    """ penalty potential energy surface calculators """

    #def __init__(self,
    #        PES1,
    #        PES2):
    #    self.PES1 = PES1
    #    self.PES2 = PES2
    #    self.alpha = 0.02*KCAL_MOL_PER_AU
    #    self.sigma = 3.5


    @staticmethod
    def from_options(**kwargs):
        """ Returns an instance of this class with default options updated from values in kwargs"""
        return Penalty_PES(Penalty_PES.default_options().set_values(kwargs))

    #def getGrad(self):
    #    avg_grad = self.PES.getGrad() 
    #    dgrad = self.PES.grada[1] - self.PES.grada[0]
    #    dgrad = dgrad.reshape((3*len(self.coords),1))

    #    prefactor = (self.dE**2. + 2.*self.alpha*self.dE)/((self.dE + self.alpha)**2.)
    #    #print prefactor
    #    #print self.PES.grada[0].flatten()
    #    #print self.PES.grada[1].flatten()
    #    #print avg_grad.T
    #    tmp = dgrad*prefactor*self.sigma
    #    #print prefactor
    #    print tmp.T
    #    print avg_grad.T
    #    grad = avg_grad + tmp
    #    print grad.T

    #    return grad

    def get_energy(self,geom):
        avgE = 0.5*(self.PES1.get_energy(geom) + self.PES2.get_energy(geom))
        self.dE = self.PES2.get_energy(geom) - self.PES1.get_energy(geom)
        #TODO what to do if PES2 is or goes lower than PES1?
        G = (self.dE**2.)/(self.dE + self.alpha)
        return avgE+self.sigma*G

    def get_gradient(self,geom):
        #print self.PES1.get_gradient(geom)
        #print np.shape( self.PES1.get_gradient(geom))
        avg_grad = 0.5*(self.PES1.get_gradient(geom) + self.PES2.get_gradient(geom))
        #print avg_grad
        dgrad = self.PES2.get_gradient(geom) - self.PES1.get_gradient(geom)
        #print dgrad
        factor = (self.dE**2. + 2.*self.alpha*self.dE)/((self.dE + self.alpha)**2.)
        return avg_grad + self.sigma*factor*dgrad


if __name__ == '__main__':
    if 0:
        from pytc import *
        import icoord as ic
        import pybel as pb
        from units import  *
        #filepath1="tests/ethylene.xyz"
        filepath2="tests/twisted_ethene.xyz"
        nocc=7
        nactive=2
        lot=PyTC.from_options(E_states=[(0,0),(0,1)],filepath=filepath2,nocc=nocc,nactive=nactive,basis='6-31gs')
        lot.cas_from_file(filepath2)

        #lot.casci_from_file_from_template(filepath1,filepath2,nocc,nocc)
        p = Penalty_PES(lot.options.copy().set_values({
            "PES":lot,
            }))
        #p.get_energy()
        #p.getGrad()
        print "alpha is %1.4f kcal/mol" % p.alpha
        mol=pb.readfile("xyz",filepath2).next()
        mol.OBMol.AddBond(6,1,1)
        print "ic1"
        ic1=ic.ICoord.from_options(mol=mol,lot=p,resetopt=False)

        for i in range(1):
            ic1.optimize(100)
            if ic1.gradrms<ic1.OPTTHRESH:
                break
            if  ic1.lot.dE>0.001*KCAL_MOL_PER_AU:
                ic1.lot.sigma *=2.
                print "increasing sigma %1.2f" % ic1.lot.sigma
        print "Finished"
    if 1:
        from molpro import *
        import icoord as ic
        import pybel as pb
        from units import  *
        filepath="tests/twisted_ethene.xyz"
        geom=manage_xyz.read_xyz(filepath,scale=1)   
        nocc=7
        nactive=2
        lot=Molpro.from_options(states=[(1,0),(1,1)],nocc=nocc,nactive=nactive,basis='6-31gs')
        pes1 = PES.from_options(lot=lot,ad_idx=0,multiplicity=1)
        pes2 = PES.from_options(lot=lot,ad_idx=1,multiplicity=1)
        #p = Penalty_PES(pes1,pes2)
        p = Penalty_PES(pes1.options.copy().set_values({
            'PES1':pes1,
            'PES2':pes2,
            }))

        #e =p.get_energy(geom)
        #print e
        #g = p.get_gradient(geom)
        #print g

        mol=pb.readfile("xyz",filepath).next()
        mol.OBMol.AddBond(6,1,1)
        print "####### ic1 ##########"
        ic1=ic.ICoord.from_options(mol=mol,PES=p,resetopt=False)
        ic1.optimize(50)

