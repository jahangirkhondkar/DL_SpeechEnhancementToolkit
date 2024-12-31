clc;
clear all;

% Reading from the Excel sheet
[x, y, Info_Sheet] = xlsread('C:\Verispeak code\collection8_filtered_NN');
disp(size(Info_Sheet));


cd('C:\Verispeak code\Neurotec_Biometric_12_4_SDK\Bin\Win32_x86');

for i = 1:size(Info_Sheet, 1) 
    i 
    gallery = Info_Sheet{i,3};
    probe = Info_Sheet{i,6};
    
    cmd = ['VerifyVoiceCS.exe ', gallery, ' ', probe];
    
    [result, cmdoutput] = system(cmd);
    
    if result == 0 
        cmdoutput = string(cmdoutput);
        splited = split(cmdoutput, ["score:", "verification"]);
        score = str2double(splited(3)) / 2;
    else
        score = 0; 
    end

    Info_Sheet{i, 8} = score;
    Info_Sheet{i, 9} = result;
end

%Writing to Excel Sheet in this directory 
cd('C:\Verispeak code\Result');

Final_score_sheet = array2table(Info_Sheet, 'VariableNames', {'Enroll_ID', 'Enroll_File', 'Enroll_Directory', 'Probe_ID', 'Probe_File', 'Probe_Directory', 'Month_Gap', 'Score', 'Output'});

Filename = 'full_collection8_filtered_NN.xlsx';
writetable(Final_score_sheet, Filename);
