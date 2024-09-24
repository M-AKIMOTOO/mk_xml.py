#!/usr/bin/env python3
# AKIMOTO
# history as below
HISTORY = """
### History of this script
 2022-02-01
 2022-02-02 update1
 2022-02-04 update2
 2022-02-05 update3
 2022-02-14 update4
 2022-02-17 update5
 2022-02-18 update6
 2022-02-21 update7
 2022-02-28 update8
 2022-03-08 update9
 2022-05-10 update10
 2022-05-15 update11
 2022-05-25 update12
 2022-05-25 update13
 2023-02-07 update14
 2023-07-15 update15
 2023-11-27 update16
 2024-01-20 update17
 2024-09-20 update18
 2024-09-24 update19

 Edit by M.AKIMOTO
### """


import re, os, sys, argparse, datetime, xml.etree.ElementTree as ET

# help
if len(sys.argv) == 1 :
    program = os.path.basename(sys.argv[0])
    os.system("%s -h" % program)
    quit()

# original def func. made by AKIMOTO
error = "\033[32mError\033[0m"
sampling_frequency = 1024e+06
class original_function :
    
    def History() :
        if history == True :
            print(HISTORY)
            quit()

    # freq code (X, C) to 8192, 6600
    def freq_conv(f) :
        if   f in ["X", "+8192e+6", "8192"] :
            freq_out = "+8192e+6"
            freq_label = "X"
        elif f in ["C", "+6600e+6", "6600"] :
            freq_out = "+6600e+6"
            freq_label = "C"
        elif f == False :
            print("%s Please specify --frequency X/C." % error)
            quit()
        else :
            print("%s %s; Such a frequency code don't exist !!" % (error, f))
            quit()
        return freq_out, freq_label
    
    # fft points check
    def fft_point_check(power_of_2) :
        fft = int(power_of_2)
        while True :
            power_of_2 = power_of_2 / 2
            if power_of_2 == 1.0 :
                break
            elif power_of_2 < 1.0 :
                print("%s %.0f; FFT points isn't power of 2 !!" % (error, fft))
                quit()
            else:
                continue

    # overlapping
    def arguments_overlapping(A1, A2) : 
        if A1 != False and A2 != False :
            print("%s you can't specify %s & %s at the same time." % (error, A1, A2))
            quit()

    # file path
    def file_check(input_file) :
        F = input_file.split()
        for file in F :
            if file != "False" :
                file_check = os.path.isfile(file)
                if file_check == True :
                    print("File exist; %s" % file)
                else :
                    print("%s %s; Such a file don't exist !!" % (error, file))
                    quit()
            else :
                continue
            
    # convert DOY to month & day
    def cal_month_day(Year_DOY) :
        doy2month_day = datetime.datetime.strptime(Year_DOY, "%y%j%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        return doy2month_day

    # display schedule list of DRG-file
    def schedule_list(num, T, R, D) :
        list_line = ""
        if drg != False and list_ == True and num == 1:
            list_line = "###\n  Observation list\n###\n"
        if drg != False and list_ == True :
            list_line = " scan %2d > %s  %s  %s\n" % (num, T, R, D)
        return list_line


# arguments
class MyHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass

description = \
"""
### USAGE
    This script make two type XML-file of your observation from DRG-file.
    First, this script make xml-file of the only fringe-finder for 
    searching fringe of your observation data then this script make 
    xml-file of all your observation schedule by using xml-file of 
    fringe-finder.
###
### EXAMPLE
    If you make xml-file of fringe-finder, you should specify 
    arguments, --drg, --scan, --length & --frequency.
    >> $ %s --drg I21001.DRG --scan 10 --length 10 --frequency X

    If you make xml-file of all the observation schedule, you 
    should specify arguments, --xml & --sample-deay at least.
    >> %s --xml I21001_10_KL.xml --sample-delay 86
###
    Please read the last message, attentions of this program !!
    Thsnks (^^), This script is made by M.AKIMOTO on 2022/02/01. 
""" % (os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0]))
epilog = \
"""
### ATTENTION
        You can not specify --drg and --xml at the same time. A new
    xml-file is made if you specify --drg, however the xml-file
    inputted by specifying --xml already inserts all the correlation 
    processing schedule. 
        In addition, you can not specify --log and --recstart at 
    the same time to. If you don't prepare octadisk-/vsrec-log files
    you can specify --recstart.
###
"""
parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=MyHelpFormatter)  

parser.add_argument("--drg"         , default=False     , type=str                                        , help="SKD ファイルの作成に用いた DRG ファイル．--xml オプションと同時に使用できない．")
parser.add_argument("--xml"         , default=False     , type=str                                        , help="一度，本プログラムを実行して出力された，フリンジファインダーのみまとめられた xml ファイル．--drg と同時に使用できない．")
parser.add_argument("--log"         , default=False     , type=str                                        , help="OCTADISK もしくは VSREC のログファイル．")
parser.add_argument("--delay"       , default="+1.6e-06", type=float                                      , help="大雑把な遅延，YI では 1.6e-06 秒とし，これがデフォルトになっている．VLBI ではこのオプションを使って 0.0 秒を指定する．")
parser.add_argument("--rate"        , default="+0.0e-00", type=float                                      , help="大雑把な遅延変化率，YI では 0.0 秒とし，これがデフォルトになっている．VLBI では Delay と Rate を補正するときに使用する．")
parser.add_argument("--fft"         , default="1024"    , type=int                                        , help="FFT 点数．２の累乗でないとエラーが出る．")
parser.add_argument("--scan"        , default=[0]       , type=int  , nargs="+"                           , help="フリンジファインダーのスキャン番号．obscode_scan_baseline.xml のファイルが出力される（それぞれは DRG ファイルによる）．")
parser.add_argument("--length"      , default="1"       , type=int                                        , help="遅延時間と遅延時間変化率の決定に用いるデータの積分時間．")
parser.add_argument("--frequency"   , default=False     , type=str  , choices=["X","8192","C","6600"]     , help="相関処理をするデータの観測周波数．")
parser.add_argument("--output"      , default="1"       , type=int                                        , help="相関出力速度．基本的に指定することはない．output = 1 は PP = 1 に相当する．")
parser.add_argument("--label"       , default=False     , type=str                                        , help="相関処理の結果がまとめられる cor ファイルに指定するラベル名前．cor ファイルは名前を書き換えることができないので，同一天体の cor ファイルを区別するなどに用いる．")
parser.add_argument("--sample-delay", default="0"       , type=float, dest="SampleDelay"                  , help="fringe コマンドの出力結果である Res-Delay の値を用いる．--xml ファイルで指定された xml ファイル中に書かれている delay と足し算が行われる．よって --xml と同時に使用しても --delay の値は用いられない．")
parser.add_argument("--sample-rate" , default="0"       , type=float, dest="SampleRate"                   , help="--delay の rate 版．")
parser.add_argument("--recorder"    , default=["vsrec"] , type=str  , nargs="+"                           , help="各局が観測に用いた記録計を指定する．例えば山口局（K）が VSREC で茨城局（H）が OCTADISK なら，-recorder K:VSREC H:OCTADISK とする．もし両方とも OCTADISK なら --recorder OCTADISK")
parser.add_argument("--recstart"    , default=False     , type=str                                        , help="--log で指定するログファイルが無い，もしくは記録開始時刻を任意で変更したいとき．--log と併用はできない．")
parser.add_argument("--baseline"    , default=False     , type=str  , choices=["H","T","K","L"], nargs="+", help="本プログラムは DRG ファイルから baseline を読み取るが，DRG ファイルの使いまわしや編集ミスで，実際に使用した観測局と異なるときに用いる．指定されたとき，その値を用いて局ごとの情報を書き込むので，引数を与え間違えると相関処理ができない．山口32m局，山口34m局，日立局，高萩局のアンテナコードで指定する．")
parser.add_argument("--type"        , default="2"       , type=int  , choices=[1, 2]                      , help="２種類の相関処理スケジュールから選択することができる．１を指定すると DRG ファイルのスケジュールごとに相関処理をする．そのため vdif を観測スケジュールのスキャンごとに分割して raw ファイルを作成しなければならない．２を指定すると，記録開始時刻を基準にしたスケジュールが作成される．こちらの場合は vdif だけでよい")
parser.add_argument("--list"        , action="store_true"                                                 , help="簡単に観測スケジュールを一覧として表示する．")
parser.add_argument("-y", "--yes"   , action="store_true"                                                 , help="本プログラムを実行すると y/n で引数の確認を促すが，不要なときにスキップするためのオプション．")
parser.add_argument("--history"     , action="store_true")

args = parser.parse_args() 
drg    = args.drg
xml    = args.xml
log    = args.log
delay  = args.delay
rate   = args.rate
fft    = args.fft
scan   = args.scan
length = args.length
freq   = args.frequency
output = args.output
label  = args.label
sample_delay = args.SampleDelay
sample_rate  = args.SampleRate
recorder = args.recorder
recstart = args.recstart
baseline = args.baseline
type_    = args.type
list_    = args.list
yes      = args.yes
history  = args.history

# arguments check
original_function.arguments_overlapping(drg, xml)
original_function.arguments_overlapping(log, recstart)

# file path check
original_function.file_check("%s %s %s" % (drg, xml, log))

# history of this script
original_function.History()


#######################
### main
#######################
if xml == False :

    # empty value & list
    i = 0
    source_line      = ""
    xml_process_line = ""
    obs_scan_list    = ""

    # convert frequency (X, C) to 8192, 6600
    freq, freq_label = original_function.freq_conv(freq)

    # FFT point check
    original_function.fft_point_check(fft)

    # REQRECSTART from octa-/vsrec-log or valuable "recstart"
    if type_ == 2 :
        if recstart == False and log != False :
            log_open = open(log, "r").readlines()
            for line in log_open :
                REQRECSTART_line = "$REQRECSTART" in line
                if REQRECSTART_line == True :
                    octa_vsrec_log_REQRECTIME = line.split()[-1]
            try :
                if not octa_vsrec_log_REQRECTIME :
                    pass
            except NameError :
                print("\"$REQRECSTART\" isn't inserted in %s." % log)
                print("Please check %s" % log)
                quit()
        elif recstart != False and log == False :
                octa_vsrec_log_REQRECTIME = recstart
        elif log == False or recstart == False :
            print("%s You must specify --log or --recstart if you specify --type=2" % error)
            quit()
        else :
            print("%s Please arguments which you input in this script." % error)
            print(epilog)
            quit()

        xml_process_line += "<!-- recstart-time of OCTADISK/VSREC from octa-/vsrec-log file; %s -->\n\n" % octa_vsrec_log_REQRECTIME

        # reference time in xml-file (its year, month & day)
        rectime_start = octa_vsrec_log_REQRECTIME

    # open DRG-file
    drg_open = open(drg, "r").readlines()

    for drg_line in drg_open :
        
        sked_line1 = "2000.0" in drg_line
        sked_line2 = "PREOB"  in drg_line
        
        if sked_line1 == True : # target coordinate
            source_name1, source_name2, ra_h, ra_m, ra_s, dec_deg, dec_m, dec_s = drg_line.split()[:8]
            source_line += f"<source name=\'{source_name1}\'><ra>{ra_h}h{ra_m}m{ra_s}</ra><dec>{dec_deg}d{dec_m}\'{dec_s}</dec></source>\n"
            if source_name2 == "$" :
                continue
            if source_name1 != source_name2 :
                source_line += f"<source name=\'{source_name2}\'><ra>{ra_h}h{ra_m}m{ra_s}</ra><dec>{dec_deg}d{dec_m}\'{dec_s}</dec></source>\n"

        elif sked_line2 == True : # target obsevation schedule
            
            i += 1
            target   = drg_line.split()[0] # the info. of DRG-file
            rectime  = drg_line.split()[4]
            duration = drg_line.split()[5]

            if baseline == False :
                baseline = drg_line.split()[9].replace("-", "")
            
            # individual xml-file
            if not scan :
                print("%s Please specify --scan." % error)
                quit()
            elif i == scan[0] :
                rectime_scan = datetime.datetime.strptime(rectime, "%y%j%H%M%S").strftime("%Y/%j %H:%M:%S")
                label = "%.0f" % i
                file_label = "%.0f" % i

            # Observation schedule list
            obs_scan_list += original_function.schedule_list(i, target.ljust(8), rectime, duration.rjust(4))

            # target length < --length
            if i == scan[0] and int(duration) < length :
                print("%s the integration time (%.0f) is longer than the duration (%s) of %s." % (error, length, duration, target))
                quit()

            if type_ == 1 :
                each_epoch_start = "20%s" % rectime
                skip_time        = 0
                if i == scan[0] :
                    duration_scan = "%s" % length # for fringe-finder
                duration_time = duration
            elif type_ == 2 :
                # calculate skip time
                rectime_datetime   = datetime.datetime.strptime(rectime, "%y%j%H%M%S")
                starttime_datetime = datetime.datetime.strptime(rectime_start, "%Y%j%H%M%S")
                differential_time  = rectime_datetime - starttime_datetime

                skip_time     = differential_time.total_seconds()
                duration_time = (int(skip_time) + int(duration))  # <length> in xml-file
                duration_scan = (int(skip_time) + length)

                each_epoch_start = rectime_start


            doy2MonthDay = original_function.cal_month_day(rectime) # convert DOY to month & day
            each_epoch_start = datetime.datetime.strptime(each_epoch_start, "%Y%j%H%M%S").strftime("%Y/%j %H:%M:%S")


            if skip_time < 0 :
                print(f"{error}: <skip> time, {skip_time:5.0f} sec, in xml-file is less than 0.")
                continue

            xml_process_line_before = "<process><epoch>%s</epoch><skip>%5.0f</skip><length>" % (each_epoch_start, skip_time)
            xml_process_line_after  = "</length><object>%8s</object><stations>%s</stations></process>" % (target, "".join(baseline))
            xml_process_line_scan_date = "<!-- scan %2d  obs-date: %s -->" % (i, doy2MonthDay)
            if i == scan[0] :
                xml_process_line += "%s%5s%s %s <!-- fringe finder -->\n" % (xml_process_line_before, duration_scan, xml_process_line_after, xml_process_line_scan_date)
                                    
            xml_process_line += "<!-- ### %s%5s%s ### --> %s\n" % (xml_process_line_before, duration_time, xml_process_line_after, xml_process_line_scan_date)

    if list_ == True :
        print(obs_scan_list)
        quit()
    if scan == 0 :
        print("%s You need to select scan number of fringe-finder to calculate \"delay\" !!" % error)
        quit()
    
    
    ant_info = {"H": ["HITACH32", "-3961788.974", "+3243597.492", "+3790597.692"], \
                "T": ["TAKAHA32", "-3961881.825", "+3243372.480", "+3790687.449"], \
                "K": ["YAMAGU32", "-3502544.587", "+3950966.235", "+3566381.192"], \
                "L": ["YAMAGU34", "-3502567.576", "+3950885.734", "+3566449.115"]}
    recording_mode = {}
    if len(recorder) == 1 :
        for baseline_key in baseline :
            recording_mode[baseline_key] = recorder[0]
        recorder = recording_mode
    else :
        for rec in recorder :
            ant_key, ant_recorder = rec.split(":")
            recording_mode[ant_key] = ant_recorder.lower()

    recorder_ant_num = sorted(list(recording_mode.keys()))
    baseline_ant_num = sorted(baseline)
    if recorder_ant_num == baseline_ant_num :
        pass
    else :
        print("%s: You mistake an argument in this program!!" % error)
        print("it is necessary that an antenna of arguments of \"--baseline\"")
        print("and \"--recorder\" are the same.")
        print(" Baseline: %s" % baseline)
        print(" Recorder: %s" % recorder)
        exit(1)
    
    xml_station1 = "\n"    
    bit_shuffle  = "\n<!-- VSREC bit shuffle -->\n"
    xml_stream_special = ""
    for baseline_key in sorted(baseline) :
        
        if recording_mode[baseline_key] == "octadisk" :
            ads = "ADS3000_OCT"
        elif recording_mode[baseline_key] == "vsrec" :
            ads = "ADS3000"
            bit_shuffle += f"<shuffle key='{baseline_key}'>24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7</shuffle>\n"
            
        xml_station1 += f"<station key='{baseline_key}'><name>{ant_info[f'{baseline_key}'][0]}</name><pos-x>{ant_info[f'{baseline_key}'][1]}</pos-x><pos-y>{ant_info[f'{baseline_key}'][2]}</pos-y><pos-z>{ant_info[f'{baseline_key}'][3]}</pos-z><terminal>{ads}</terminal></station>\n"

        xml_stream_special += f"<special key='{baseline_key}'><sideband>LSB</sideband></special>\n"
    
    xml_station1 = xml_station1 + bit_shuffle


    # parameter check
    print("###")
    print(" recorder  : %s" % recorder)
    print(" octa-log  : %s" % log     )
    print(" DRG-file  : %s" % drg     )
    print(" Scan      : %s" % scan[0] )
    print(" FFT       : %s" % fft     )
    print(" Delay     : %s" % delay   )
    print(" Rate      : %s" % rate    )
    print(" Length    : %s" % length  )
    print(" Baseline  : %s" % baseline)
    print(" Frequency : %s" % freq    )
    print("###")
    # yes or no
    if yes != True:
        while True:
            answer = input("Are the above paramters correct ? [y/n] : ")
            if answer == "y":
                break
            elif answer == "n" :
                print("### Please start over !")
                quit()
            else :
                print(">> The answer is \"y\" or \"n\"")
elif xml != False : # make xml-file of all scan

    xml_all = ""
    file_label = "scan"
    
    xml_open = open(xml, "r").readlines()

    xml_all_scan_line = 0
    
    # edit individual xml-file
    for xml_line in xml_open :
        
        if "<!-- ###" in xml_line : # xml-file all schedule <process>*</process>
            
            xml_all_scan_line += 1
            if 0 in scan :
                pass
            elif not xml_all_scan_line in scan :
                continue
            
            commentout_left  = re.findall("<!-- ###", xml_line)
            commentout_right = re.findall("### -->" , xml_line)
            xml_line = xml_line.replace("%s " % commentout_left[0] , "")
            xml_line = xml_line.replace("%s"  % commentout_right[0], "")
            xml_all += xml_line #(xml_line.split("\n")[0] + "  <!-- selected scan -->\n")
            
             
        elif "<!-- fringe finder -->" in xml_line :
            continue
        elif "<!-- selected scan -->" in xml_line :
            continue
        else :
            xml_all += xml_line
    
    xml_root = ET.fromstring(xml_all)

    xml_clock_line = xml_root.find("clock")
    xml_all_delay  = float(xml_clock_line.find("delay").text)
    xml_all_rate   = float(xml_clock_line.find("rate").text)

    xml_stream_line   = xml_root.find("stream")
    xml_all_label     = xml_stream_line.find("label").text
    xml_all_fft       = xml_stream_line.find("fft").text
    xml_all_output    = xml_stream_line.find("output").text
    xml_all_frequency = float(xml_stream_line.find("frequency").text)

    xml_process_line  = xml_root.find("process")
    xml_all_baseline  = xml_process_line.find("stations").text

    xml_all_total_delay = str(xml_all_delay + sample_delay / sampling_frequency)
    xml_all_total_rate  = str(xml_all_rate  + sample_rate  / xml_all_frequency)

    # label in all
    if label == False :
        #label = "all"
        label = original_function.freq_conv("%d" % (int(xml_all_frequency/1e6)))[1].lower()#.replace("-","")
    # fft in all
    if fft != "1024" :
        original_function.fft_point_check(fft) # check
        xml_stream_line.find("fft").text = str(fft)
    # output in all
    if output != "1" :
        xml_all_output = output
    if not 0 in scan :
        xml_out_label = "%s" % "_".join(list(map(str, scan)))
    elif label != False :
        xml_out_label = label
    else :
        xml_out_label = "all"
    
    _, freq_label = freq, freq_label = original_function.freq_conv("%s" % int(xml_all_frequency/1000000))

    xml_stream_line.find("label").text = label
    xml_clock_line.find("delay").text = xml_all_total_delay
    xml_clock_line.find("rate").text  = xml_all_total_rate
    

    # make xml-file of all scan Ver.
    xml_name = "./%s_%s_%s_%s.xml" % (os.path.basename(xml).split("_")[0], xml_out_label, xml_all_baseline, freq_label)
    xml_all = ET.tostring(xml_root, encoding='utf-8').decode(encoding='utf-8') # return XML as String
    with open(xml_name, mode='w') as out_file:
        ET.canonicalize(xml_all, out=out_file, with_comments=True)

    """ old version

    xml_save = open(xml_name, "w")
    xml_save.write(xml_all)
    xml_save.close()
    """
        
    # parameter check
    print("###")
    print(" xml-file    : %s" % xml)
    print(" fft         : %s" % fft)
    print(" total delay : %s" % xml_all_total_delay)
    print(" total rate  : %s" % xml_all_total_rate)
    print(" frequency   : %+3.3e" % xml_all_frequency)
    print(" stations    : %s" % xml_all_baseline)
    print(" label       : %s" % label)
    print(" output      : %s" % output)
    print("###")
    
    print("make file > %s" % xml_name)
    quit()


# xml-file header, clock, stream
xml_header = \
"""<?xml version='1.0' encoding='UTF-8' ?>
<schedule>"""

xml_ADS = \
"""
<terminal name='ADS1000'><speed>1024000000</speed><channel> 1</channel><bit>2</bit><level>-1.5,+0.5,-0.5,+1.5</level></terminal>
<terminal name='ADS3000'><speed>1024000000</speed><channel>1</channel><bit>2</bit><level>-1.5,-0.5,+0.5,+1.5</level></terminal>  
<terminal name='ADS3000_OCT'><speed>1024000000</speed><channel>1</channel><bit>2</bit><level>-1.5,+0.5,-0.5,+1.5</level></terminal>"""

xml_stream = \
"""<stream>
<label>%s</label><frequency>%s</frequency><channel>1</channel><fft>%s</fft><output>%s</output>
%s</stream>
""" % (label, freq, fft, output, xml_stream_special) # L = label, F1 = frequency, F2 = FFT, O = output

xml_clock = "<clock key='%s'><epoch>%s</epoch><delay>%s</delay><rate>%s</rate></clock> <!-- scan %.0f -->\n" % (baseline[-1], rectime_scan, delay, rate, scan[0])

# make xml-file
xml_base = os.path.splitext(os.path.basename(drg))[0]
xml_name = "%s_%.0f_%s_%s.xml" % (xml_base, scan[0], "".join(baseline), freq_label)
xml_save = open(xml_name, "w")
xml_save.write("%s\n" % xml_header)
xml_save.write("%s\n" % xml_ADS)
xml_save.write("%s\n" % xml_station1)
xml_save.write("%s\n" % source_line)
xml_save.write("%s\n" % xml_stream)
xml_save.write("%s\n" % xml_clock)
xml_save.write("%s\n" % xml_process_line)
xml_save.write("</schedule>")
xml_save.close()

print("make file > %s" % xml_name)

