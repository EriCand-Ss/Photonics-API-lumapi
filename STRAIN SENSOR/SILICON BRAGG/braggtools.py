import numpy as np

def documentation():
    ''' this function prints the documentation of the module
    it is used to print the documentation of the module
    when the module is imported'''
    print('This module contains functions to create and simulate Bragg gratings in EME.')
    print('The functions are:')
    print('phase(n, emeApi, L_pd, width_ridge, thick_Si, material_Si)')
    print('bigFirst(x, grtId, emeApi, L_pd, width_ridge, thick_Si, material_Si, Delta_W)')
    print('smallFirst(x, grtId, emeApi, L_pd, width_ridge, thick_Si, material_Si, Delta_W)')
    print('buildBraggGrating(phase_nmbr, L_pd, emeApi, width_ridge, thick_Si, material_Si, Delta_W)')

def phase(n,emeApi,L_pd,width_ridge,thick_Si,material_Si):
    ''' this function creates a phase section
    n: phase section number
    L_pd: period length
    width_ridge: ridge width
    thick_Si: silicon thickness
    material_Si: silicon material
    emeApi: the Api object'''
    m = np.arange(1, 99, 2)
    N = m[n - 1]
    # in order to draw the phase sections its needed
    # to map the phase section number to the next odd number
    # by doing this the phase section will be positioned properly
    # as its multiplied by the correct number of periods
    # even tho using np arange is not the most efficient way, it works
    emeApi.addrect()
    emeApi.set('x min', L_pd * N)
    emeApi.set('x max', L_pd * N + L_pd)
    emeApi.set('y', 0)
    emeApi.set('y span', width_ridge)
    emeApi.set('z', 0)
    emeApi.set('z span', thick_Si)
    emeApi.set('material', material_Si)
    emeApi.set('name', f'grt_phase_section{n}')
    return 0


def bigFirst(x, grtId, emeApi,L_pd,width_ridge,thick_Si,material_Si,Delta_W):
    # bragg grating
    emeApi.addrect()
    emeApi.set('x min', x)
    emeApi.set('x max', x + L_pd / 2)
    emeApi.set('y', 0)
    emeApi.set('y span', width_ridge + Delta_W)
    emeApi.set('z', 0)
    emeApi.set('z span', thick_Si)
    emeApi.set('material', material_Si)
    emeApi.set('name', f'grt_big{grtId}')

    emeApi.addrect()
    emeApi.set('x', emeApi.getnamed(f'grt_big{grtId}', 'x') + L_pd / 2)
    emeApi.set('x span', L_pd / 2)
    emeApi.set('y', 0)
    emeApi.set('y span', width_ridge - Delta_W)
    emeApi.set('z', 0)
    emeApi.set('z span', thick_Si)
    emeApi.set('material', material_Si)
    emeApi.set('name', f'grt_small{grtId}')
    return 0


def smallFirst(x, grtId, emeApi,L_pd,width_ridge,thick_Si,material_Si,Delta_W):
    emeApi.addrect()
    emeApi.set('x min', x)
    emeApi.set('x max', x + L_pd / 2)
    emeApi.set('y', 0)
    emeApi.set('y span', width_ridge - Delta_W)
    emeApi.set('z', 0)
    emeApi.set('z span', thick_Si)
    emeApi.set('material', material_Si)
    emeApi.set('name', f'grt_small{grtId}')

    emeApi.addrect()
    emeApi.set('x', emeApi.getnamed(f'grt_small{grtId}', 'x') + L_pd / 2)
    emeApi.set('x span', L_pd / 2)
    emeApi.set('y', 0)
    emeApi.set('y span', width_ridge + Delta_W)
    emeApi.set('z', 0)
    emeApi.set('z span', thick_Si)
    emeApi.set('material', material_Si)
    emeApi.set('name', f'grt_big{grtId}')

    return 0

def buildBraggGrating(phase_nmbr, L_pd,emeApi,width_ridge,thick_Si,material_Si,Delta_W):

    ''' this function builds a bragg grating cell by using the other functions
    in the module
    '''
    for i in range(0, phase_nmbr + 1, 1):
        if i % 2 == 0:
            bigFirst(2 * i * L_pd, i,emeApi,L_pd,width_ridge,
                     thick_Si,material_Si,Delta_W)
        else:
            smallFirst(2 * i * L_pd, i,emeApi,L_pd,width_ridge,
                       thick_Si,material_Si,Delta_W)
        if i == phase_nmbr:
            break
        else:
            phase(i + 1,emeApi,L_pd,width_ridge,thick_Si,material_Si)
    # cell creation
    emeApi.selectpartial('grt')
    emeApi.addtogroup('grt_cell')
    emeApi.select('grt_cell')
    emeApi.redrawoff()
    emeApi.selectpartial('grt_cell')
    emeApi.addtogroup('Bragg grating')
    emeApi.redrawon()
    emeApi.unselectall()  # it shouldn't be necessary, but it doesnt work without it

def addSolver(emeApi,phase_nmbr, width_ridge, thick_BOX,L_pd, periods, material_BOX, Delta_W):
    '''
    This function explores the bragg grating periodicity
    to solve the bragg grating transmission problem by using the EME solver.
    '''
    emeApi.addeme()

    nmbr_grts = phase_nmbr + 1
    nmbr_cells = phase_nmbr + 2*nmbr_grts
    periodic_groups = phase_nmbr + 1

    #### cells setup
    group_cells = phase_nmbr + 2 * (phase_nmbr + 1)
    cells = np.ones(group_cells)
    cells = cells.reshape(-1, 1)
    cells = np.block(cells)
    ####
    ####periods setup
    periods = np.array(periods).reshape(-1, 1)
    periods = np.block(periods)
    ###
    ### group spans setup
    group_spans = []
    for i in range(1, phase_nmbr + 1, 1):
        group_spans.append(L_pd / 2)
        group_spans.append(L_pd / 2)
        group_spans.append(L_pd)
        if i == phase_nmbr:
            group_spans.append(L_pd / 2)
            group_spans.append(L_pd / 2)
    group_spans = np.array(group_spans).reshape(-1, 1)
    group_spans = np.block(group_spans)
    ###


    emeApi.set('x min', emeApi.getnamed('Bragg grating::grt_cell::grt_big0', 'x min'))
    emeApi.set('y', 0)
    emeApi.set('y span', 2e-6)
    emeApi.set('z', 0)
    emeApi.set('z span', 2e-6)

    emeApi.set('energy conservation', 'conserve energy')
    emeApi.set('number of cell groups', nmbr_cells)
    emeApi.set('number of periodic groups', periodic_groups)

    emeApi.set('group spans', group_spans)
    emeApi.set('cells', cells)
    emeApi.set('display cells', 1)

    emeApi.set('periods', periods)

    ### periodicity optimization
    start_cell = []
    for i in range(1,group_cells, 3):
        start_cell.append(i)
    start_cell = np.array(start_cell).reshape(-1, 1)
    start_cell = np.block(start_cell)
    emeApi.set('start cell group', start_cell)

    end_cell = []
    for i in range(2, group_cells+1, 3):
        end_cell.append(i)
    end_cell = np.array(end_cell).reshape(-1, 1)
    end_cell = np.block(end_cell)
    emeApi.set('end cell group', end_cell)

    ###
    emeApi.set('wavelength', 1.55*1e-6)
    emeApi.set('background material', material_BOX)

    ## boundaries
    emeApi.set('y min bc', 'PML')
    emeApi.set('y max bc', 'PML')
    emeApi.set('z min bc', 'PML')
    emeApi.set('z max bc', 'PML')

    ## mesh
    emeApi.addmesh()
    emeApi.set('y', 0)
    emeApi.set('z', 0)
    emeApi.set('x min', emeApi.getnamed('Bragg grating::grt_cell::grt_big0', 'x min') - 0.5e-06)
    emeApi.set('x max', emeApi.getnamed(f'Bragg grating::grt_cell::grt_big{phase_nmbr}', 'x max') + 0.5e-06)
    emeApi.set('y span', (width_ridge + Delta_W) * 1.2)

    return 0



##### Interconnect ######

def CreateCircuit(icApi,n_detectors,c,lasers_wavelengths):
    ''' this function creates the interconnect circuit
    icApi: the Api object
    n_detectors: number of detectors/lasers/filters
    c: speed of light
    lasers_wavelengths: list of the wavelengths of the lasers'''
    icApi.addelement('Bragg_optimized')
    icApi.set('name', 'Bragg')
    icApi.setposition('Bragg', 240, 130)
    for i in range(2):
        icApi.addelement('Optical Splitter/Coupler')
        icApi.set('name', f'Splitter/Coupler {i + 1}')
    for i in range(2):
        icApi.rotateelement(f'Splitter/Coupler 1')
    icApi.setposition('Splitter/Coupler 1', -20, 0)
    icApi.setposition('Splitter/Coupler 2', 500, 0)

    for i in range(1, n_detectors + 1, 1):
        icApi.addelement('PIN Photodetector')
        icApi.set('name', f'Photodetector {i}')
        icApi.addelement('CW Laser')
        icApi.set('name', f'Laser {i}')
        icApi.addelement('Power Meter')
        icApi.set('name', f'Power Meter {i}')
        icApi.addelement('Rectangular Optical Filter')
        icApi.set('name', f'Filter {i}')
    icApi.select('Splitter/Coupler 1')
    icApi.set('number of ports', n_detectors)
    icApi.select('Splitter/Coupler 2')
    icApi.set('number of ports', n_detectors)
    # positioning
    for i in range(1, n_detectors + 1, 1):
        icApi.setposition(f'Laser {i}', -200, -250 + (i - 1) * 150)
        icApi.setposition('Splitter/Coupler 1', 0, 0)
        icApi.setposition(f'Filter {i}', 850, -100 + (i - 1) * 150)
        icApi.setposition(f'Photodetector {i}', 1000, -100 + (i - 1) * 150)
        icApi.setposition(f'Power Meter {i}', 1150, -150 + (i - 1) * 150)
    # connections
    for i in range(1, n_detectors + 1, 1):
        icApi.connect(f'Laser {i}', 'output', 'Splitter/Coupler 1', f'port {i + 1}')
        icApi.connect(f'Filter {i}', 'input', 'Splitter/Coupler 2', f'port {i + 1}')
        icApi.connect(f'Filter {i}', 'output', f'Photodetector {i}', 'input')
        icApi.connect(f'Photodetector {i}', 'output', f'Power Meter {i}', 'input')
    icApi.connect('Splitter/Coupler 1', 'port 1', 'Bragg', 'port 1')
    icApi.connect('Bragg', 'port 2', 'Splitter/Coupler 2', 'port 1')
    icApi.switchtolayout()
    for i in range(1, n_detectors + 1, 1):
        icApi.select(f'Laser {i}')
        icApi.set('frequency', c / (lasers_wavelengths[i - 1]))
        icApi.select(f'Filter {i}')
        icApi.set('frequency', c / (lasers_wavelengths[i - 1]))
    #probe wavelength
    '''
    icApi.select(f'Laser {n_detectors}')
    icApi.set('frequency', c/(wl2))
    icApi.select(f'Filter {n_detectors}')
    icApi.set('frequency', c/(wl2))'''
    return 0

def func_extra(bt,importlib,EMEAPI, PHASE_NB, LPD, WIDTH_RIDGE, DELTA_W,THICK_SI, MATERIAL_SI, THICK_BOX,PERIODS,MATERIAL_BOX,MESH_MULTIPLIER,START_WVG,STOP_WVG,NUMBER_POINTS,TEMP):

    EMEAPI.switchtolayout()
    EMEAPI.deleteall()
    bt.buildBraggGrating(emeApi=EMEAPI, phase_nmbr=PHASE_NB, L_pd=LPD, width_ridge=WIDTH_RIDGE, Delta_W=DELTA_W,
                            thick_Si=THICK_SI, material_Si=MATERIAL_SI)
        
    importlib.reload(bt)
    EMEAPI.delete('EME')
    bt.addSolver(emeApi=EMEAPI, phase_nmbr=PHASE_NB,
                    width_ridge=WIDTH_RIDGE, thick_BOX=THICK_BOX,
                    L_pd=LPD, periods=PERIODS,
                    material_BOX=MATERIAL_BOX,Delta_W=DELTA_W)
    EMEAPI.set("set maximum mesh step", 1)
    EMEAPI.set('dx', MESH_MULTIPLIER)
    EMEAPI.set('dy', MESH_MULTIPLIER)
    EMEAPI.set('dz', MESH_MULTIPLIER)
    EMEAPI.select("EME")
    EMEAPI.set("simulation temperature",TEMP)
    EMEAPI.save('optimizedSimulation')
    EMEAPI.run()
    EMEAPI.setemeanalysis('wavelength sweep', 1)
    EMEAPI.setemeanalysis('start wavelength', START_WVG)
    EMEAPI.setemeanalysis('stop wavelength', STOP_WVG)
    EMEAPI.setemeanalysis('number of wavelength points', NUMBER_POINTS)


    EMEAPI.emesweep('wavelength sweep')
    Resultado = EMEAPI.getemesweep("S_wavelength_sweep")

    R, S11M, S11F,S21M,S21F =np.abs(Resultado['s11'])**2,np.abs(Resultado['s11']),np.angle(Resultado['s11']),np.abs(Resultado['s21']),np.angle(Resultado['s21'])
    return R, S11M,S11F,S21M,S21F