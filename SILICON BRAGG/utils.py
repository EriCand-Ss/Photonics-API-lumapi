import numpy as np

def achar_x_e_y_maximo_em_um_intervalo_quando_tiver_varios_picos(funcao, x, xmin, xmax):
    # Esta funcao analisa o maior valor de "funcao" dentro do intervalo xmin<=x<=xmax retornando x e y onde ocorreu maximo de funcao.
    # funcao - Array na qual deseja-se encontrar o maximo valor. variavel dependente
    # x - Array que sera varrido. variavel independente
    # xmin - float valor inicial
    # xmax - float valor final

    mask = (x >= xmin) & (x <= xmax) #mask eh um vetor modificado de x, sendo limitado no intervalo fornecido
    
    if not np.any(mask): #se o intervalo fornecido nao condizer com o vetor x, retorna None
        return None, None
    
    funcao_intervalo = funcao[mask] #funcao_intervalo eh um vetor modificado de "funcao". basicamente eh "funcao" truncado na "mask"
    x_intervalo = x[mask] #procura o maximo dentro de funcao_intervalo
    index = np.argmax(funcao_intervalo)  #indice onde o maximo ocorreu na primeira vez.
    x_maximo = x_intervalo[index] #x_maximo eh o valor de x para o maximo achado

    y_maximo = funcao_intervalo[index] #y_maximo eh o valor de y para o maximo achado

    return round(x_maximo,6),round(y_maximo,6) #eh retornado os valores com aproximacao de 6 casas decimais

def analise_comprimento_de_onda_para_sensor(parametro_variavel, Transmissao, comprimento_de_onda, x_min,x_max):
    # Essa funcao obtem as transmissoes em funcao do comprimento de onda para cada parametro variavel (temperatura ou strain) e retorna dois Arrays: 
    # um para comprimento de onda de pico e outro para transmissao de pico onde houve pico de transmissao para cada parametrovariavel. 

    # parametro_variavel - Array com o parametro que esta sendo variado. Ex: pressao, temperatura, tensao, deformacao. 
    # transmissao - Array de array com a transmissao para cada parametro variado. len(transmissao) == len(parametro_variavel)
    # comprimento_de_onda - Array com os comprimentos de onda. len(transmissao[i])==len(comprimento_de_onda)
    # x_min - float valor minimo do intervalo
    # x_max - float valor maximo do intervalo

    frequencia_onde_ocorre_maxima_transmissao = np.zeros(len(parametro_variavel))
    Amplitude_onde_ocorre_maxima_transmissao = np.zeros(len(parametro_variavel))

    for i in range(len(parametro_variavel)):
        x_pico, y_pico = achar_x_e_y_maximo_em_um_intervalo_quando_tiver_varios_picos(Transmissao[i],comprimento_de_onda, x_min,x_max)
        frequencia_onde_ocorre_maxima_transmissao[i] = (x_pico)
        Amplitude_onde_ocorre_maxima_transmissao[i] = (y_pico)
    
    return frequencia_onde_ocorre_maxima_transmissao, Amplitude_onde_ocorre_maxima_transmissao

def funcao_que_gera_o_ambiente_de_simulacao_e_calcula_a_potencia_na_saida_de_n_laser(inter,x_1,defasagem,diretorio_dos_parametros_S):
        # funcao cria ambiente de simulacao no INTERCONNECT composto por dois laser, um combiner, um dispositivo arbitrario (a depender do parametro S),
        #  um splitter, dois filtros, dois fotodectores e dois medidores de potencia. Posteriormente simula e retorna os valores de potencia lidos nos medidores de potencia.

        # inter - referente a funcao da API lumapi. inter = lumapi.INTERCONNECT().
        # x_1 - float - comprimento de onda do laser 1.
        # defasagem - float - comprimento de onda defasado de x_1. a soma defasagem+x_1 eh o comprimento de onda do laser 2.
        # diretorio_dos_parametros_S - string - diretorio com o nome do arquivo com parametro S .dat
         
        inter.switchtolayout()
        inter.deleteall()

        inter.addelement("CW Laser")
        inter.set("name", "fonte2")
        inter.set("frequency", 3e8/(x_1+defasagem))

        inter.addelement("CW Laser")
        inter.set("name", "fonte1")
        inter.set("frequency", 3e8/((x_1)))

        inter.addelement("Optical Combiner")
        inter.set("name", "optC1")

        inter.addelement("Optical Combiner")
        inter.set("configuration", "splitter")
        inter.set("name", "optS1")
        inter.rotateelement("optS1")
        inter.rotateelement("optS1")

        inter.addelement("Optical N Port S-Parameter")
        inter.set("name","spars1")
        inter.set("load from file", True)
        inter.set("s parameters filename", diretorio_dos_parametros_S)

        inter.addelement("Rectangular Optical Filter")
        inter.set("name","filter1")
        inter.set("frequency", 3e8/(x_1))

        inter.addelement("Rectangular Optical Filter")
        inter.set("name","filter2")
        inter.set("frequency", 3e8/((x_1+defasagem)))

        inter.addelement("PIN Photodetector")
        inter.set("name", "photodec1")
        inter.addelement("PIN Photodetector")
        inter.set("name", "photodec2")

        inter.addelement("Power Meter")
        inter.set("name", "PM1")
        inter.addelement("Power Meter")
        inter.set("name","PM2")

        inter.setposition("fonte1", 0,0)
        inter.setposition("fonte2", 0,200)

        inter.setposition("optC1", 200,100)
        inter.setposition("spars1", 400,100)
        inter.setposition("optS1", 600,100)

        inter.setposition("filter1", 800,0)
        inter.setposition("filter2", 800,200)

        inter.setposition("photodec1", 1000,0)
        inter.setposition("photodec2", 1000,200)

        inter.setposition("PM1", 1200,0)
        inter.setposition("PM2", 1200,200)

        inter.connect("fonte2", "output", "optC1", "input 2")
        inter.connect("fonte1", "output", "optC1", "input 1")

        inter.connect("optC1", "output", "spars1", "port 1")
        inter.connect("spars1", "port 2", "optS1", "input")

        inter.connect("filter1", "input", "optS1", "output 2")
        inter.connect("filter2", "input", "optS1", "output 1")

        inter.connect("photodec1", "input", "filter1", "output")
        inter.connect("photodec2", "input", "filter2", "output")

        inter.connect("PM1", "input", "photodec1", "output")
        inter.connect("PM2", "input", "photodec2", "output")

        inter.run()

        return (inter.getresult("PM1","total power")),(inter.getresult("PM2","total power"))

def bragg_integrado_simples(emeApi,Lambda,W_great,W_small,thickness,w_box,t_box,material_Si,material_BOX,wvg_start,wvg_stop,nb,
                                        Temperatura=300,periods=150, comprimento_de_onda = 1500e-9,mesh_multiplier=5):

    # Simulacao via EME, que retorna refletância, |S11|, fase de S11, |S21| e fase de S21
    # Lambda - float - eh o comprimento de um periodo de bragg
    # W_great - float - largura maior
    # W_small - float - largura menor
    # thickness - float - espessura 
    # w_box - largura do solver EME
    # t_box - espessura do solver EME
    # material_Si - string - material do core
    # material_BOX - string - material do background
    # wvg_start - float - comprimento de onda de inicio da simulacao
    # wvg_stop - float - comprimento de onda do final da simulacao
    # nb - int - quantidade de pontos a serem simulados
    # Temperatura - float - Temperatura da simulacao
    # periods - float - quantidade de periodos de bragg
    # comprimento de onda - float - comprimento de onda de parametro para a simulacao
    # mesh multiplier - int - multiplicador da malha de simulacao

    emeApi.switchtolayout()
    emeApi.deleteall()

    #bragg grating
    emeApi.addrect()
    emeApi.set('x', -Lambda/4)
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_great)
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_big')

    emeApi.addrect()
    emeApi.set('x', Lambda/4 )
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_small )
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_small')

    emeApi.addeme()
    emeApi.set("simulation temperature", Temperatura)
    emeApi.set("solver type", "3D: X prop")
    emeApi.set("energy conservation", "conserve energy")
    emeApi.set("background material", material_BOX)
    emeApi.set("x", 0)
    emeApi.set('z', 0)
    emeApi.set('y', 0)

    emeApi.set("x min", -Lambda/2 )
    emeApi.set('y span', w_box )
    emeApi.set('z span', t_box )

    emeApi.set("number of cell groups", 2)
    emeApi.set("number of modes for all cell groups", 1)
    emeApi.set("group spans" , np.array([Lambda/2 ,
                                        Lambda/2 ]))
    emeApi.set("display cells",1)

    emeApi.set("number of periodic groups", 1)
    emeApi.set("start cell group", 1)
    emeApi.set("end cell group", 2)
    emeApi.set("periods", periods)

    emeApi.set("wavelength", comprimento_de_onda)

    emeApi.addmesh()
    emeApi.set("x", 0)
    emeApi.set('z', 0)
    emeApi.set('y', 0)
    emeApi.set('x span', Lambda)
    emeApi.set('y span', w_box)
    emeApi.set('z span', t_box)
    emeApi.set("set mesh multiplier", 1)
    emeApi.set('x mesh multiplier', mesh_multiplier)
    emeApi.set('y mesh multiplier', mesh_multiplier)
    emeApi.set('z mesh multiplier', mesh_multiplier)

    emeApi.run()

    emeApi.setemeanalysis("wavelength sweep", 1)
    emeApi.setemeanalysis("start wavelength",wvg_start)
    emeApi.setemeanalysis("stop wavelength",wvg_stop)
    emeApi.setemeanalysis("number of wavelength points", nb)
    emeApi.emesweep("wavelength sweep")

    Resultado = emeApi.getemesweep("S_wavelength_sweep")
    
    return np.abs(Resultado['s11'])**2,np.abs(Resultado['s11']),np.angle(Resultado['s11']),np.abs(Resultado['s21']),np.angle(Resultado['s21'])

def construir_bragg_e_retornar_indices_efetivos(emeApi,L_pd,W_great,W_small,thickness,material_Si,material_BOX,w_fde,t_fde,w_mesh,t_mesh,
                    Temperatura = 300,mesh_multiplier=5):
    
    # Simulacao via FDE, que retorna indices de grupo e efetivo na regiao de alto e baixo indice na grade de bragg
    # L_pd - float - eh o comprimento de cada guia. eh um valor arbitrario maior que 0. pode ser literalmente qualquer valor
    # W_great - float - largura maior 
    # W_small - float - largura menor
    # thickness - float - espessura 
    # w_fde - float - largura do solver FDE
    # t_fde - float - espessura do solver FDE
    # w_mesh - float - largura do mesh
    # t_mes - float - espessura do mesh
    # material_Si - string - material do core
    # material_BOX - string - material do background
    # Temperatura - float - Temperatura da simulacao
    # mesh multiplier - int - multiplicador da malha de simulacao

    emeApi.switchtolayout()
    emeApi.deleteall()

    #bragg grating
    emeApi.addrect()
    emeApi.set('x', -L_pd/4)
    emeApi.set('x span', L_pd/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_great)
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_big')

    emeApi.addrect()
    emeApi.set('x', L_pd/4)
    emeApi.set('x span', L_pd/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_small)
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_small')

    emeApi.selectpartial('grt')
    emeApi.addtogroup('grt_cell')
    emeApi.select('grt_cell')
    emeApi.selectpartial('grt_cell')
    emeApi.addtogroup('bragg')

    emeApi.addfde()
    emeApi.set("simulation temperature", Temperatura)
    emeApi.set("background material", material_BOX)
    emeApi.set("solver type", "2D X normal")
    emeApi.set("y min bc", "Anti-Symmetric")
    emeApi.set("y max bc", "Metal")
    emeApi.set("z min bc", "Symmetric")
    emeApi.set("y max bc", "Metal")
    emeApi.set('x',-L_pd/4)
    emeApi.set('z', 0)
    emeApi.set('y', 0)
    emeApi.set('y span', w_fde)
    emeApi.set('z span', t_fde)

    emeApi.addmesh()
    emeApi.set("x", 0)
    emeApi.set('z', 0)
    emeApi.set('y', 0)
    emeApi.set('x span', L_pd)
    emeApi.set('y span', w_mesh)
    emeApi.set('z span', t_mesh)
    emeApi.set("set mesh multiplier", 1)
    emeApi.set('x mesh multiplier', mesh_multiplier)
    emeApi.set('y mesh multiplier', mesh_multiplier)
    emeApi.set('z mesh multiplier', mesh_multiplier)

    emeApi.save("Bragg")

    emeApi.switchtolayout()
    emeApi.select("FDE")
    emeApi.set("x", L_pd/4)
    emeApi.findmodes()

    group_index_high = np.abs(emeApi.getresult("FDE::data::mode1", "ng")[0][0])
    neff_high = np.abs(emeApi.getresult("FDE::data::mode1", "neff")[0][0])

    emeApi.switchtolayout()
    emeApi.select("FDE")
    emeApi.set("x", -L_pd/4)
    emeApi.findmodes()

    group_index_low = np.abs(emeApi.getresult("FDE::data::mode1", "ng")[0][0])
    neff_low = np.abs(emeApi.getresult("FDE::data::mode1", "neff")[0][0])

    return group_index_high,neff_high,group_index_low,neff_low


def bragg_integrado_com_phase_shifter(emeApi,Lambda,W_great,W_small,width,thickness,w_box,t_box,material_Si,material_BOX,wvg_start,wvg_stop,nb,
                                        Temperatura=300,periods=150, comprimento_de_onda = 1500e-9,mesh_multiplier=5, Phases =1):

    # Simulacao via EME, que retorna refletância, |S11|, fase de S11, |S21| e fase de S21
    # Lambda - float - eh o comprimento de um periodo de bragg
    # W_great - float - largura maior
    # W_small - float - largura menor
    # thickness - float - espessura 
    # w_box - largura do solver EME
    # t_box - espessura do solver EME
    # material_Si - string - material do core
    # material_BOX - string - material do background
    # wvg_start - float - comprimento de onda de inicio da simulacao
    # wvg_stop - float - comprimento de onda do final da simulacao
    # nb - int - quantidade de pontos a serem simulados
    # Temperatura - float - Temperatura da simulacao
    # periods - float - quantidade de periodos de bragg
    # comprimento de onda - float - comprimento de onda de parametro para a simulacao
    # mesh multiplier - int - multiplicador da malha de simulacao

    emeApi.switchtolayout()
    emeApi.deleteall()

    #bragg grating
    emeApi.addrect()
    emeApi.set('x', -Lambda/4)
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_great)
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_big1')

    emeApi.addrect()
    emeApi.set('x', Lambda/4 )
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_small )
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_small1')

    emeApi.addrect()
    emeApi.set('x', Lambda )
    emeApi.set('x span', Lambda)
    emeApi.set('y',0)
    emeApi.set('y span', width )
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'p_shifter')

    emeApi.addrect()
    emeApi.set('x', 2*Lambda+Lambda/4)
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_great)
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_big2')

    emeApi.addrect()
    emeApi.set('x', 2*Lambda - Lambda/4 )
    emeApi.set('x span', Lambda/2)
    emeApi.set('y',0)
    emeApi.set('y span', W_small )
    emeApi.set('z',0)
    emeApi.set('z span', thickness)
    emeApi.set('material', material_Si)
    emeApi.set('name', 'grt_small2')

    if(Phases == 2 or Phases == 3):
        emeApi.addrect()
        emeApi.set('x', 3*Lambda )
        emeApi.set('x span', Lambda)
        emeApi.set('y',0)
        emeApi.set('y span', width )
        emeApi.set('z',0)
        emeApi.set('z span', thickness)
        emeApi.set('material', material_Si)
        emeApi.set('name', 'p_shifter2')

        emeApi.addrect()
        emeApi.set('x', 3*Lambda+3*Lambda/4)
        emeApi.set('x span', Lambda/2)
        emeApi.set('y',0)
        emeApi.set('y span', W_great)
        emeApi.set('z',0)
        emeApi.set('z span', thickness)
        emeApi.set('material', material_Si)
        emeApi.set('name', 'grt_big3')

        emeApi.addrect()
        emeApi.set('x', 3*Lambda+3*Lambda/4+Lambda/2 )
        emeApi.set('x span', Lambda/2)
        emeApi.set('y',0)
        emeApi.set('y span', W_small )
        emeApi.set('z',0)
        emeApi.set('z span', thickness)
        emeApi.set('material', material_Si)
        emeApi.set('name', 'grt_small3')
        if(Phases == 3):
            emeApi.addrect()
            emeApi.set('x', 5*Lambda )
            emeApi.set('x span', Lambda)
            emeApi.set('y',0)
            emeApi.set('y span', width )
            emeApi.set('z',0)
            emeApi.set('z span', thickness)
            emeApi.set('material', material_Si)
            emeApi.set('name', 'p_shifter3')

            emeApi.addrect()
            emeApi.set('x', 5*Lambda+5*Lambda/4)
            emeApi.set('x span', Lambda/2)
            emeApi.set('y',0)
            emeApi.set('y span', W_great)
            emeApi.set('z',0)
            emeApi.set('z span', thickness)
            emeApi.set('material', material_Si)
            emeApi.set('name', 'grt_big4')

            emeApi.addrect()
            emeApi.set('x', 5*Lambda+5*Lambda/4-Lambda/2)
            emeApi.set('x span', Lambda/2)
            emeApi.set('y',0)
            emeApi.set('y span', W_small )
            emeApi.set('z',0)
            emeApi.set('z span', thickness)
            emeApi.set('material', material_Si)
            emeApi.set('name', 'grt_small4')

    emeApi.addeme()
    emeApi.set("simulation temperature", Temperatura)
    emeApi.set("solver type", "3D: X prop")
    emeApi.set("energy conservation", "conserve energy")
    emeApi.set("background material", material_BOX)
    emeApi.set("x", 0)
    emeApi.set('z', 0)
    emeApi.set('y', 0)

    emeApi.set("x min", -Lambda/2 )
    emeApi.set('y span', w_box )
    emeApi.set('z span', t_box )

    if (Phases == 2):
        emeApi.set("number of cell groups", 8)
        emeApi.set("number of modes for all cell groups", 1)
        emeApi.set("group spans" , np.array([Lambda/2 ,
                                            Lambda/2 ,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2]))
    elif(Phases == 1):
        emeApi.set("number of cell groups", 5)
        emeApi.set("number of modes for all cell groups", 1)
        emeApi.set("group spans" , np.array([Lambda/2 ,
                                            Lambda/2 ,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2]))
    elif(Phases == 3):
        emeApi.set("number of cell groups", 11)
        emeApi.set("number of modes for all cell groups", 1)
        emeApi.set("group spans" , np.array([Lambda/2 ,
                                            Lambda/2 ,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2,
                                            Lambda,
                                            Lambda/2 ,
                                            Lambda/2]))
        
    emeApi.set("display cells",1)

    if(Phases == 2):
        emeApi.set("number of periodic groups", 3)
        emeApi.set("start cell group", np.array([1,4,7]))
        emeApi.set("end cell group", np.array([2,5,8]))
        emeApi.set("periods", periods)

    elif(Phases == 1):
        
        emeApi.set("number of periodic groups", 2)
        emeApi.set("start cell group", np.array([1,4]))
        emeApi.set("end cell group", np.array([2,5]))
        emeApi.set("periods", periods)
    elif(Phases == 3):
        
        emeApi.set("number of periodic groups", 4)
        emeApi.set("start cell group", np.array([1,4,7,10]))
        emeApi.set("end cell group", np.array([2,5,8,11]))
        emeApi.set("periods", periods)

    emeApi.set("wavelength", comprimento_de_onda)

    emeApi.addmesh()
    emeApi.set("x", Phases*Lambda)
    emeApi.set('x span', (Phases*2+1)*Lambda)

    emeApi.set('z', 0)
    emeApi.set('y', 0)
    emeApi.set('y span', w_box)
    emeApi.set('z span', t_box)
    emeApi.set("set mesh multiplier", 1)
    emeApi.set('x mesh multiplier', mesh_multiplier)
    emeApi.set('y mesh multiplier', mesh_multiplier)
    emeApi.set('z mesh multiplier', mesh_multiplier)

    emeApi.run()

    emeApi.setemeanalysis("wavelength sweep", 1)
    emeApi.setemeanalysis("start wavelength",wvg_start)
    emeApi.setemeanalysis("stop wavelength",wvg_stop)
    emeApi.setemeanalysis("number of wavelength points", nb)
    emeApi.emesweep("wavelength sweep")

    Resultado = emeApi.getemesweep("S_wavelength_sweep")
    
    return np.abs(Resultado['s11'])**2,np.abs(Resultado['s11']),np.angle(Resultado['s11']),np.abs(Resultado['s21']),np.angle(Resultado['s21'])
