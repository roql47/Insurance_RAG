import { useState, useMemo } from 'react'

function TreatmentCodeSearch() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchFilter, setSearchFilter] = useState('all') // 'all', 'code', 'name', 'edi'
  const [codeType, setCodeType] = useState('treatment') // 'treatment', 'material', 'medicine'
  const [sortConfig, setSortConfig] = useState({ key: 'code', direction: 'asc' })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 100

  // 치료코드 데이터
  const treatmentData = [
    { code: 'FE0720', name: 'Cardiac catheterization(Rt)-Congenital Cardiac Abnormalies', edi: 'EDI001' },
    { code: 'FE0721', name: 'Cardiac catheterization(Rt)-Others', edi: 'EDI002' },
    { code: 'FE0722', name: 'Cardiac catheterization(Lt)-Congenital Cardiac Abnormalies', edi: 'EDI003' },
    { code: 'FE0723', name: 'Cardiac catheterization(Lt)-Others', edi: 'EDI004' },
    { code: 'FE0724', name: 'Left Cardiac Catheterization through Atrial Septal Puncture(RT 포함)Congenital Cardiac Abnormalies', edi: 'EDI005' },
    { code: 'FE0725', name: 'Left Cardiac Catheterization through Atrial Septal Puncture(RT 포함) Others', edi: 'EDI006' },
    { code: 'FE0726', name: 'Cardiac Catheterization through Patent Foramen Ovale-Congenital Cardiac Abnormalies', edi: 'EDI007' },
    { code: 'FE0727', name: 'Cardiac Catheterization through Patent Foramen Ovale-Others', edi: 'EDI008' },
    { code: 'FE0728', name: 'Pulmonary Vasoreactivity Test', edi: 'EDI009' },
    { code: 'FE0729', name: 'Balloon Occlusion Test', edi: 'EDI010' },
    { code: 'FE0730', name: '관상동맥내 압력측정술(단일혈관)', edi: 'EDI011' },
    { code: 'FE0731', name: '관상동맥내 압력측정술(추가혈관)', edi: 'EDI012' },
    { code: 'FE6551', name: 'Implantation of Insertable Loop Recoder', edi: 'EDI013' },
    { code: 'FE6552', name: 'Removal of Insertable Loop Recoder', edi: 'EDI014' },
    { code: 'FE707001', name: '[급여외90%]Local Transcutaneous Oxygen Pressure Measurement', edi: 'EDI015' },
    { code: 'FE7247', name: '임상전기생리학적검사：기본적 Basic [히스속전기도검사포함]', edi: 'EDI016' },
    { code: 'FE7248', name: '임상전기생리학적검사：좌심방 또는 관상정맥동에 삽입한 전극도자를 통한 조율 및 기록', edi: 'EDI017' },
    { code: 'FE7249', name: '임상전기생리학적검사：좌심실에 삽입한 전극도자를 통한 조율 및 기록', edi: 'EDI018' },
    { code: 'FE7250', name: '임상전기생리학적검사：계획된 전기자극에 의한 부정맥의 유발검사', edi: 'EDI019' },
    { code: 'FE7251', name: '히스속전기도검사', edi: 'EDI020' },
    { code: 'FE7252', name: '임상전기생리학적검사 종합적(히스속전기도검사포함)', edi: 'EDI021' },
    { code: 'FE7253', name: '임상전기생리학적검사 추적(히스속전기도검사포함)', edi: 'EDI022' },
    { code: 'FE7259', name: '임상전기생리학적검사：정맥 주사 약물투입 후에 시행하는 계획적 조율 자극', edi: 'EDI023' },
    { code: 'FEX87202', name: 'ICD programming', edi: 'EDI024' },
    { code: 'FEX873', name: 'Coronary Spasm Study', edi: 'EDI025' },
    { code: 'FMC0003', name: 'Intracardiac Electrophysiologic 3-Dimensional Mapping[NAVX)', edi: 'EDI026' },
    { code: 'FMC0008', name: 'Intracoronary OCT', edi: 'EDI027' },
    { code: 'FMC0011', name: '[심장뇌혈관]심도자법컴퓨터기록-Angiography', edi: 'EDI028' },
    { code: 'FMC0012', name: '[심장뇌혈관]심도자법컴퓨터기록-Intervention', edi: 'EDI029' },
    { code: 'GC8060T', name: 'Pericardiocentesis [PCC]', edi: 'EDI030' },
    { code: 'GEB40210', name: '[동][급여외80%]V-scan Echocardiography', edi: 'EDI031' },
    { code: 'GEB40211', name: '[동][급여외80%](CA)(단순Ⅱ) 천자부위,카테터삽입위치 확인', edi: 'EDI032' },
    { code: 'GEB40213', name: '[급여외80%](RD)(단순Ⅱ) 천자부위,카테터삽입위치 확인', edi: 'EDI033' },
    { code: 'GEB56102', name: '(RD)(유도Ⅰ)US-심낭천자', edi: 'EDI034' },
    { code: 'GEB56107', name: '(RD)(유도Ⅰ)낭종흡인,흉막천자,심낭천자,양수천자등', edi: 'EDI035' },
    { code: 'GEB61201', name: '[급여외80%]Intracardiac Echocardiography', edi: 'EDI036' },
    { code: 'JM0651', name: '자654-1(나)주2 : Cryoablation of Arrhythmia -Atrial fibrillation(냉각풍선절제술 실시한경우)', edi: 'EDI037' },
    { code: 'JM0652', name: '자654-1주2 : Cryoablation of Arrhythmia -Atrial fibrillation(냉각풍선절제술시 중격천자 시행한 경우)', edi: 'EDI038' },
    { code: 'JM0653', name: '자654-1주2 : Cryoablation of Arrhythmia(Septal puncture) -Supraventricular Arrhythmia', edi: 'EDI039' },
    { code: 'JM0654', name: '[봉X]Radiofrequency Ablation Of Atrial Fibrillation 선형절제술을 실시한 경우', edi: 'EDI040' },
    { code: 'JM0655', name: '자654-1주2 : Cryoablation of Arrhythmia(Septal puncture) -Atrial fibrillation', edi: 'EDI041' },
    { code: 'JM0656', name: '자654-1주2 : Cryoablation of Arrhythmia(Septal puncture) -Atrioventricular nodal, His bundle ablation', edi: 'EDI042' },
    { code: 'JM0657', name: '자654-1가 : Cryoablation of Arrhythmia -Supraventricular Arrhythmia', edi: 'EDI043' },
    { code: 'JM0658', name: '자654-1나 : Cryoablation of Arrhythmia -Atrial fibrillation', edi: 'EDI044' },
    { code: 'JM0659', name: '자654-1(나)주1 : Cryoablation of Arrhythmia -Atrial fibrillation(선형절제술 실시한 경우)', edi: 'EDI045' },
    { code: 'JM0661', name: '자654-1다 : Cryoablation of Arrhythmia -Ventricular Arrhythmia', edi: 'EDI046' },
    { code: 'JM0662', name: '자654-1라 : Cryoablation of Arrhythmia -Atrioventricular nodal, His bundle ablation', edi: 'EDI047' },
    { code: 'JM166101', name: '[심장뇌혈관]Embolization Cerebral Aneurysm(Assisted)', edi: 'EDI048' },
    { code: 'JM166201', name: '[심장뇌혈관]Embolization Cerebral Aneurysm(Others)', edi: 'EDI049' },
    { code: 'JM6510', name: 'Percutaneous Closure Of Patent Ductus Arteriosus', edi: 'EDI050' },
    { code: 'JM6511', name: 'Percutaneous Left Atrial Appendage Occlusion[본인부담80]', edi: 'EDI051' },
    { code: 'JM6513', name: '자651-3: Percutaneous Closure of Muscular Ventricular Septal Defect', edi: 'EDI052' },
    { code: 'JM6521', name: 'Balloon Percutaneous Atrial Septostomy', edi: 'EDI053' },
    { code: 'JM6522', name: 'Blade Percutaneous Atrial Septostomy', edi: 'EDI054' },
    { code: 'JM6531', name: 'Percutaneous Valvuloplasty(Mitral Valve)', edi: 'EDI055' },
    { code: 'JM6532', name: 'Percutaneous Valvuloplasty(Aortic Valve)', edi: 'EDI056' },
    { code: 'JM6533', name: 'Percutaneous Valvuloplasty(Pulmonic Valve)', edi: 'EDI057' },
    { code: 'JM6540', name: 'Intracardiac Electrophysiologic 3-Dimensional Mapping(Supraventricular Arrhythmia)심방세동,중격천자', edi: 'EDI058' },
    { code: 'JM6541', name: 'Radiofrequency Ablation Of Supraventricular Arrhthmia', edi: 'EDI059' },
    { code: 'JM6542', name: 'Radiofrequency Ablation Of Atrial Fibrillation', edi: 'EDI060' },
    { code: 'JM6543', name: 'Radiofrequency Ablation Of Ventricular Arrhthmia', edi: 'EDI061' },
    { code: 'JM6544', name: 'Radiofrequency Ablation Of Supraventricular Arrhthmia(Septal Puncture)', edi: 'EDI062' },
    { code: 'JM6545', name: 'Radiofrequency Ablation Of Atrial Fibrillation(Septal Puncture)', edi: 'EDI063' },
    { code: 'JM6546', name: '(Navx)Intracardiac Electrophysiologic 3-Dimensional Mapping(Supraventricular Arrhythmia)', edi: 'EDI064' },
    { code: 'JM6547', name: '(Navx)Intracardiac Electrophysiologic 3-Dimensional Mapping(Supraventricular Arrhythmia)심방세동실시', edi: 'EDI065' },
    { code: 'JM6548', name: '(Navx)Intracardiac Electrophysiologic 3-Dimensional Mapping(Ventricular Arrhythmia)', edi: 'EDI066' },
    { code: 'JM6549', name: 'Intracardiac Electrophysiologic 3-Dimensional Mapping(Supraventricular Arrhythmia)중격천자 실시', edi: 'EDI067' },
    { code: 'JM6550', name: 'Radiofrequency Ablation Of Arrhthmia-Atrioventricular nodal, His bundle ablation', edi: 'EDI068' },
    { code: 'JM6551', name: 'Percutaneous Transluminal Coronary Angioplasty(Single Vessel )', edi: 'EDI069' },
    { code: 'JM6552', name: 'Percutaneous Transluminal Coronary Angioplasty(Additional Vessel)', edi: 'EDI070' },
    { code: 'JM6553', name: 'PTCA of Culprit lesion in acute myocardial infarction', edi: 'EDI071' },
    { code: 'JM6554', name: 'PTCA of Chronic Total Occlusion', edi: 'EDI072' },
    { code: 'JM6556', name: 'Radiofrequency Ablation Of Arrhthmia-Atrioventricular nodal, His bundle ablation(Septal Puncture)', edi: 'EDI073' },
    { code: 'JM6561', name: 'Percutaneous Transcatheter Placement Of Intracoronary Stent(Single Vessel)', edi: 'EDI074' },
    { code: 'JM6562', name: 'Percutaneous Transcatheter Placement Of Intracoronary Stent(Additional Vessel)', edi: 'EDI075' },
    { code: 'JM6563', name: 'Percutaneous Transcatheter Placement Of Intracoronary Stent(Single Vessel)(+PTCA,Percutaneous Transluminal Coronary Atherectomy)', edi: 'EDI076' },
    { code: 'JM6564', name: 'Percutaneous Transcatheter Placement Of Intracoronary Stent(Additionl Vessel)(+PTCA,Percutaneous Transluminal Coronary Atherectomy)', edi: 'EDI077' },
    { code: 'JM6565', name: 'PCI of Culprit lesion in acute myocardial infarction', edi: 'EDI078' },
    { code: 'JM6566', name: 'PCI of Chronic Total Occlusion', edi: 'EDI079' },
    { code: 'JM6567', name: 'PCI of Chronic Total Occlusion(PTCA 및 죽상반절제술 동시)', edi: 'EDI080' },
    { code: 'JM6571', name: 'Percutaneous Transluminal Coronary Atherectomy (Single Vessel)', edi: 'EDI081' },
    { code: 'JM6572', name: 'Percutaneous Transluminal Coronary Atherectomy(Additional Vessel', edi: 'EDI082' },
    { code: 'JM6580', name: '[본인부담80]Transapical Approach Transcatheter Aortic Valve Implantation', edi: 'EDI083' },
    { code: 'JM6581', name: '[본인부담80]Transaortic Approach Transcatheter Aortic Valve Implantation', edi: 'EDI084' },
    { code: 'JM6582', name: '[본인부담80]Transfemoral, Transsubclavian Approach Transcatheter Aortic Valve Implantation', edi: 'EDI085' },
    { code: 'JM6585', name: 'Percutaneous Pulmonary Valve Implantation', edi: 'EDI086' },
    { code: 'JM6590', name: '자659-2 : Resuscitative Endovascular Balloon Occlusion of the Aorta(REBOA)', edi: 'EDI087' },
    { code: 'JM659702', name: 'Percutaneous Transluminal Angioplasty, Others-Lower Ext', edi: 'EDI088' },
    { code: 'JM659901', name: '[심장뇌혈관]Percutaneous Cerebral Angioplasty with Drug', edi: 'EDI089' },
    { code: 'JM660203', name: '[심장뇌혈관]Percutaneous Intravascular Installation Of Metallic Stent (Carotid)', edi: 'EDI090' },
    { code: 'JM6603', name: '[봉X]Percutaneous Intravascular Installation Of Metallic Stent (Aortic)', edi: 'EDI091' },
    { code: 'JM6604', name: '[봉X]Percutaneous Intravascular Installation Of Metallic Stent (Pulmonary)', edi: 'EDI092' },
    { code: 'JM6605', name: '[봉X]Percutaneous Intravascular Installation Of Metallic Stent (Others)', edi: 'EDI093' },
    { code: 'JM6611', name: '[봉X]Percutaneous Intravascular Installation Of Stent-Graft(Aortic)', edi: 'EDI094' },
    { code: 'JM6612', name: '[봉X]Percutaneous Intravascular Installation Of Stent-Graft(Aortic-Iliac)', edi: 'EDI095' },
    { code: 'JM6613', name: '[봉X]Percutaneous Intravascular Installation Of Stent-Graft(Others)', edi: 'EDI096' },
    { code: 'JM6620', name: '[봉X]M909Percutaneous Intravascular Atherectomy', edi: 'EDI097' },
    { code: 'JM6632', name: '[봉X]Thrombolytic Treatment (Other Vessels)', edi: 'EDI098' },
    { code: 'JM6634', name: '[봉X]Percutaneous Coronary Artery Thrombolytic Treatment', edi: 'EDI099' },
    { code: 'JM6638', name: '[봉X]Mechanical Thrombolysis Coronary Artery', edi: 'EDI100' },
    { code: 'JM663801', name: 'Mechanical Thrombolysis(관상동맥)-PCI동시시행 35%', edi: 'EDI101' },
    { code: 'JM6639', name: '[봉X]Mechanical Thrombolysis Others', edi: 'EDI102' },
    { code: 'JM6644', name: '[봉X]Embolization Other Vessels', edi: 'EDI103' },
    { code: 'JM6650', name: '[봉X]Percutaneous Inferior Vena Cava Filter Placement', edi: 'EDI104' },
    { code: 'JM665001', name: '경피적 하대정맥여과기 제거술', edi: 'EDI105' },
    { code: 'JM6651', name: 'Endograft Fixation -경피적 혈관내 스텐트이식 설치술시 그래프트 고정', edi: 'EDI106' },
    { code: 'JM6652', name: 'Endograft Fixation -경피적 혈관내 스텐트이식 설치술후 그래프트 고정', edi: 'EDI107' },
    { code: 'JMY762', name: 'Fluoroscopic Foreign Body Removal', edi: 'EDI108' },
    { code: 'JO0203', name: 'Implantation Of Internal Pulse Generator with Atrial or Ventricular Lead(Single Chamber)', edi: 'EDI109' },
    { code: 'JO0204', name: 'Implantation Of Internal Pulse Generator with Atrial and Ventricular Lead(Dual Chamber)', edi: 'EDI110' },
    { code: 'JO0205', name: 'Replacement of Pacemaker Pulse Generator Atrial or Ventricular Lead(Single Chamber)', edi: 'EDI111' },
    { code: 'JO0206', name: 'Replacement of Pacemaker Pulse Generator Atrial and Ventricular Lead(Dual Chamber System)', edi: 'EDI112' },
    { code: 'JO0207', name: 'Conversion of Single Chamber System to Dual Chamber System', edi: 'EDI113' },
    { code: 'JO0208', name: 'Removal Pacemaker Pulse Generator', edi: 'EDI114' },
    { code: 'JO0209', name: 'Removal Pacemaker Lead(Single Chamber System)', edi: 'EDI115' },
    { code: 'JO0210', name: 'Removal Pacemaker Lead(Dual Chamber System)', edi: 'EDI116' },
    { code: 'JO0211', name: 'Implantaion Of Cardiovertor Defibrillator[Transvenous]', edi: 'EDI117' },
    { code: 'JO0212', name: 'Replacement of ICD Generator only[Transvenous]', edi: 'EDI118' },
    { code: 'JO0213', name: 'Electronic Analysis of ICD System Atrial or Ventricular Lead(Single Chamber)', edi: 'EDI119' },
    { code: 'JO0214', name: 'Electronic Analysis of ICD System  Atrial and Ventricular Lead(Dual Chamber System)', edi: 'EDI120' },
    { code: 'JO0219', name: '자200-2(4)(가) : Removal of ICD Generator Only[Transvenous]', edi: 'EDI121' },
    { code: 'JO0220', name: '자200-2(4)(나) : Removal of ICD ventricle lead[Transvenous]', edi: 'EDI122' },
    { code: 'JO0221', name: '자200-2(4)(다) : Removal of ICD atrium and ventricle lead[Transvenous]', edi: 'EDI123' },
    { code: 'JO0222', name: '자200-2(5) : ICD lead reposition[Transvenous]', edi: 'EDI124' },
    { code: 'JO1903', name: 'ECMO Extra Corporeal Membrane Oxygenator(시술당일)', edi: 'EDI125' },
    { code: 'JO190301', name: '(CV)ECMO Extra Corporeal Membrane Oxygenator(시술당일)', edi: 'EDI126' },
    { code: 'JO2001', name: 'Setting Of Cardiac Pacing With External Pulse Generator', edi: 'EDI127' },
    { code: 'JO2009', name: 'Implantation of Internal Pulse Generator Pacemaker - Lead reposition', edi: 'EDI128' },
    { code: 'JO2211', name: 'Implantation of Cardioverter Defibrillator[Subcutaneous]', edi: 'EDI129' },
    { code: 'JO2212', name: 'Replacement of ICD Generator only[Subcutaneous]', edi: 'EDI130' },
    { code: 'JO2214', name: 'Removal of ICD Generator Only[Subcutaneous]', edi: 'EDI131' },
    { code: 'JO2215', name: 'Removal of ICD lead[Subcutaneous]', edi: 'EDI132' },
    { code: 'JO2216', name: 'ICD lead reposition[Subcutaneous]', edi: 'EDI133' },
    { code: 'JOZ751', name: 'Percutaneous  Closure Of Interatrial Septal Defect', edi: 'EDI134' },
    { code: 'RAHA60105', name: '[심장뇌혈관]Vertebral Angiography', edi: 'EDI135' },
    { code: 'RAHA60105G', name: '[심장뇌혈관]3-Vessel Angiography( PACS 제외)', edi: 'EDI136' },
    { code: 'RAHA60106G', name: '[심장뇌혈관]3-Vessel 50% Angiography ( PACS 제외)', edi: 'EDI137' },
    { code: 'RAHA60107G', name: '3 Vessel Angiography', edi: 'EDI138' },
    { code: 'RAHA60303', name: '[심장뇌혈관]External Carotid Angiography', edi: 'EDI139' },
    { code: 'RAHA60403', name: '[심장뇌혈관]Internal Carotid Angiography', edi: 'EDI140' },
    { code: 'RAHA60404', name: '[심장뇌혈관]Internal Carotid(both) Angiography both', edi: 'EDI141' },
    { code: 'RAHA60505', name: '[심장뇌혈관]4-Vessel Angiography', edi: 'EDI142' },
    { code: 'RAHA610', name: 'Right Atriography', edi: 'EDI143' },
    { code: 'RAHA611', name: '(심혈관센터)Right Ventriculography', edi: 'EDI144' },
    { code: 'RAHA613', name: 'Left Atriography', edi: 'EDI145' },
    { code: 'RAHA614', name: 'Pulmonary Arteriography', edi: 'EDI146' },
    { code: 'RAHA615', name: 'Thoracic Aortography', edi: 'EDI147' },
    { code: 'RAHA618', name: 'Internal Mammary Arteriography', edi: 'EDI148' },
    { code: 'RAHA621', name: 'Abdominal Arteriography', edi: 'EDI149' },
    { code: 'RAHA63301', name: '(심장혈관센터)Selective Pelvic Arteriography', edi: 'EDI150' },
    { code: 'RAHA641', name: 'Brachial Arteriography', edi: 'EDI151' },
    { code: 'RAHA642', name: 'Retrograde Arteriography of Upper Extremity', edi: 'EDI152' },
    { code: 'RAHA651', name: 'Femoral Arteriography', edi: 'EDI153' },
    { code: 'RAHA652', name: 'Extremity Arteriography', edi: 'EDI154' },
    { code: 'RAHA670', name: 'Coronary Angiography', edi: 'EDI155' },
    { code: 'RAHA680', name: '(심혈관센터)Aortocoronary Venous Bypass Graft Angiography', edi: 'EDI156' },
    { code: 'RAHA681', name: '(심혈관센터)Aortocoronary Venous Bypass Graft Angiography(2개혈관부터)', edi: 'EDI157' },
    { code: 'RAHA682', name: '이식된관동맥우회로조영촬영[환자본래의관상동맥조영촬영포함]과 동시촬영된좌심실조영촬영', edi: 'EDI158' },
    { code: 'RGG043002', name: 'Fluoroscopy(진단적)혈관촬영실', edi: 'EDI159' },
    { code: 'RRDU032', name: 'US Intravascular (US) (IVUS)', edi: 'EDI160' },
    { code: 'W0003', name: '(예약)Cardiac CAG(PCI+PTCA+Angio)PACS SYSTEM', edi: 'EDI161' },
    { code: 'W0006', name: '(예약) Cardiac EP PACS SYSTEM', edi: 'EDI162' },
    { code: 'W0012', name: '(예약) Cardiac Report CDIS SYSTEM', edi: 'EDI163' },
    { code: 'W0191', name: '(예약)Pheripheral PAG(PTA+Angio)PACS연동용', edi: 'EDI164' },
    { code: 'W0192', name: '(예약)EVAR(Endovascular Aneurysm Repair+TEVAR)PACS연동용', edi: 'EDI165' },
    { code: 'W0194', name: '(예약)NS+NU PACS연동(심뇌혈관)', edi: 'EDI166' }
  ]

  // 재료코드 데이터
  const materialData = [
    { code: 'M0001', name: '스텐트 - 약물용출성 관상동맥용', edi: 'MAT001' },
    { code: 'M0002', name: '스텐트 - 금속 관상동맥용', edi: 'MAT002' },
    { code: 'M0003', name: '벌룬카테터 - PTCA용', edi: 'MAT003' },
    { code: 'M0004', name: '벌룬카테터 - 약물방출형', edi: 'MAT004' },
    { code: 'M0005', name: '가이드와이어 - 관상동맥용', edi: 'MAT005' },
    { code: 'M0006', name: '심박동기 - 단심방형', edi: 'MAT006' },
    { code: 'M0007', name: '심박동기 - 양심실형', edi: 'MAT007' },
    { code: 'M0008', name: '제세동기 - 이식형', edi: 'MAT008' },
    { code: 'M0009', name: '인공심장판막 - 기계판막', edi: 'MAT009' },
    { code: 'M0010', name: '인공심장판막 - 생체판막', edi: 'MAT010' },
    { code: 'M0011', name: '대동맥판 - 경피적 이식용', edi: 'MAT011' },
    { code: 'M0012', name: '폐색기 - 좌심방이 폐색용', edi: 'MAT012' },
    { code: 'M0013', name: '폐색기 - 심방중격결손 폐색용', edi: 'MAT013' },
    { code: 'M0014', name: '카테터 - 전극도자', edi: 'MAT014' },
    { code: 'M0015', name: '카테터 - 냉각풍선', edi: 'MAT015' }
  ]

  // 약제코드 데이터
  const medicineData = [
    { code: 'D0001', name: 'Heparin 주사제 5000IU/5mL', edi: 'MED001' },
    { code: 'D0002', name: 'Aspirin 정제 100mg', edi: 'MED002' },
    { code: 'D0003', name: 'Clopidogrel 정제 75mg', edi: 'MED003' },
    { code: 'D0004', name: 'Ticagrelor 정제 90mg', edi: 'MED004' },
    { code: 'D0005', name: 'Prasugrel 정제 10mg', edi: 'MED005' },
    { code: 'D0006', name: 'Warfarin 정제 5mg', edi: 'MED006' },
    { code: 'D0007', name: 'Rivaroxaban 정제 20mg', edi: 'MED007' },
    { code: 'D0008', name: 'Apixaban 정제 5mg', edi: 'MED008' },
    { code: 'D0009', name: 'Dabigatran 캡슐 150mg', edi: 'MED009' },
    { code: 'D0010', name: 'Atorvastatin 정제 20mg', edi: 'MED010' },
    { code: 'D0011', name: 'Rosuvastatin 정제 10mg', edi: 'MED011' },
    { code: 'D0012', name: 'Nitroglycerin 설하정 0.6mg', edi: 'MED012' },
    { code: 'D0013', name: 'Metoprolol 정제 50mg', edi: 'MED013' },
    { code: 'D0014', name: 'Carvedilol 정제 25mg', edi: 'MED014' },
    { code: 'D0015', name: 'Amlodipine 정제 5mg', edi: 'MED015' }
  ]

  // 선택된 코드 타입에 따른 데이터
  const currentData = useMemo(() => {
    switch (codeType) {
      case 'material':
        return materialData
      case 'medicine':
        return medicineData
      default:
        return treatmentData
    }
  }, [codeType])

  // 필터링 및 정렬
  const filteredAndSortedData = useMemo(() => {
    // 검색 필터링
    let filtered = currentData.filter(item => {
      if (!searchTerm) return true
      
      const term = searchTerm.toLowerCase()
      
      switch (searchFilter) {
        case 'code':
          return item.code.toLowerCase().includes(term)
        case 'name':
          return item.name.toLowerCase().includes(term)
        case 'edi':
          return item.edi.toLowerCase().includes(term)
        default: // 'all'
          return item.code.toLowerCase().includes(term) ||
                 item.name.toLowerCase().includes(term) ||
                 item.edi.toLowerCase().includes(term)
      }
    })

    // 정렬
    filtered.sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]
      
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1
      }
      return 0
    })

    return filtered
  }, [currentData, searchTerm, searchFilter, sortConfig])

  // 페이지네이션
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage)
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return filteredAndSortedData.slice(startIndex, startIndex + itemsPerPage)
  }, [filteredAndSortedData, currentPage])

  // 페이지 변경 시 스크롤 상단으로
  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // 코드 타입 변경 시 페이지 초기화
  const handleCodeTypeChange = (type) => {
    setCodeType(type)
    setCurrentPage(1)
  }

  // 검색 시 페이지 초기화
  const handleSearchChange = (value) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) {
      return '⇅'
    }
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white shadow-sm overflow-hidden mb-6 border border-stone-200">
          <div className="bg-stone-700 p-6 sm:p-8 border-b border-stone-600">
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              코드 조회 시스템
            </h1>
            <p className="mt-2 text-stone-300 text-sm">
              치료코드, 재료코드, 약제코드 및 EDI 정보를 조회하세요
            </p>
          </div>

          {/* 코드 타입 선택 */}
          <div className="p-6 sm:p-8 bg-amber-50 border-b border-stone-200">
            <div className="flex gap-2">
              <button
                onClick={() => handleCodeTypeChange('treatment')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  codeType === 'treatment'
                    ? 'bg-stone-700 text-white'
                    : 'bg-white text-stone-700 border border-stone-300 hover:bg-stone-50'
                }`}
              >
                치료코드
              </button>
              <button
                onClick={() => handleCodeTypeChange('material')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  codeType === 'material'
                    ? 'bg-stone-700 text-white'
                    : 'bg-white text-stone-700 border border-stone-300 hover:bg-stone-50'
                }`}
              >
                재료코드
              </button>
              <button
                onClick={() => handleCodeTypeChange('medicine')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  codeType === 'medicine'
                    ? 'bg-stone-700 text-white'
                    : 'bg-white text-stone-700 border border-stone-300 hover:bg-stone-50'
                }`}
              >
                약제코드
              </button>
            </div>
          </div>

          {/* 검색 바 */}
          <div className="p-6 sm:p-8 bg-white border-b border-stone-200">
            <div className="flex gap-3 mb-3">
              <select
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="px-4 py-3 border border-stone-300 bg-white text-stone-700 focus:ring-2 focus:ring-stone-500 focus:border-stone-500"
              >
                <option value="all">전체</option>
                <option value="code">코드</option>
                <option value="name">검사코드명</option>
                <option value="edi">EDI</option>
              </select>
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="검색어를 입력하세요..."
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="w-full px-4 py-3 pl-12 border border-stone-300 focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                />
                <svg
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-stone-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <p className="text-stone-600">
                총 <span className="font-semibold text-stone-900">{filteredAndSortedData.length}</span>개의 항목
                {filteredAndSortedData.length > itemsPerPage && (
                  <span className="ml-2 text-stone-500">
                    (페이지 {currentPage} / {totalPages})
                  </span>
                )}
              </p>
              {searchTerm && (
                <button
                  onClick={() => handleSearchChange('')}
                  className="text-stone-600 hover:text-stone-700 font-medium"
                >
                  초기화
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 테이블 */}
        <div className="bg-white shadow-sm overflow-hidden border border-stone-200">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-stone-200">
              <thead className="bg-stone-50">
                <tr>
                  <th
                    onClick={() => handleSort('code')}
                    className="px-6 py-4 text-left text-xs font-semibold text-stone-700 uppercase tracking-wider cursor-pointer hover:bg-stone-100 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      코드
                      <span className="text-stone-400">{getSortIcon('code')}</span>
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('name')}
                    className="px-6 py-4 text-left text-xs font-semibold text-stone-700 uppercase tracking-wider cursor-pointer hover:bg-stone-100 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      검사코드명
                      <span className="text-stone-400">{getSortIcon('name')}</span>
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('edi')}
                    className="px-6 py-4 text-left text-xs font-semibold text-stone-700 uppercase tracking-wider cursor-pointer hover:bg-stone-100 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      EDI
                      <span className="text-stone-400">{getSortIcon('edi')}</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-stone-200">
                {paginatedData.map((item, index) => (
                  <tr
                    key={index}
                    className="hover:bg-amber-50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-stone-700">
                      {item.code}
                    </td>
                    <td className="px-6 py-4 text-sm text-stone-900">
                      {item.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-stone-600 font-mono">
                      {item.edi}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 검색 결과 없음 */}
          {filteredAndSortedData.length === 0 && (
            <div className="text-center py-12 bg-amber-50">
              <svg
                className="mx-auto h-12 w-12 text-stone-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-base font-semibold text-stone-900 mb-1">검색 결과 없음</h3>
              <p className="text-sm text-stone-500">다른 검색어를 입력해보세요.</p>
            </div>
          )}
        </div>

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center">
            <nav className="flex items-center gap-1">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`px-3 py-2 border text-sm font-medium ${
                  currentPage === 1
                    ? 'bg-stone-100 text-stone-400 cursor-not-allowed'
                    : 'bg-white text-stone-700 hover:bg-stone-50 border-stone-300'
                }`}
              >
                이전
              </button>
              
              {/* 페이지 번호 */}
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(page => {
                  // 현재 페이지 주변 5개만 표시
                  return (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 2 && page <= currentPage + 2)
                  )
                })
                .map((page, index, array) => {
                  // ... 표시
                  if (index > 0 && array[index - 1] !== page - 1) {
                    return (
                      <span key={`ellipsis-${page}`} className="px-3 py-2 text-stone-500">
                        ...
                      </span>
                    )
                  }
                  
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-4 py-2 border text-sm font-medium ${
                        currentPage === page
                          ? 'bg-stone-700 text-white border-stone-700'
                          : 'bg-white text-stone-700 hover:bg-stone-50 border-stone-300'
                      }`}
                    >
                      {page}
                    </button>
                  )
                })}
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`px-3 py-2 border text-sm font-medium ${
                  currentPage === totalPages
                    ? 'bg-stone-100 text-stone-400 cursor-not-allowed'
                    : 'bg-white text-stone-700 hover:bg-stone-50 border-stone-300'
                }`}
              >
                다음
              </button>
            </nav>
          </div>
        )}

        {/* 푸터 */}
        <div className="mt-8 pt-4 border-t border-stone-200 text-center">
          <p className="text-base text-stone-600 font-semibold mb-1">
            중앙대학교광명병원 AI 프롬프톤 & AWS supported
          </p>
          <p className="text-xs text-stone-500">
            © 2025 Insurance RAG System. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}

export default TreatmentCodeSearch

