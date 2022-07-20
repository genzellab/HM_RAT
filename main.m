%% preprocessing

%% 1 - set up the stage
clear all
close all

addpath('/home/genzel/Desktop//Emanuele/artifact_detector')
addpath('/home/genzel/Desktop/Emanuele/artifact_detector/fieldtrip')
addpath('/home/genzel/Desktop/Emanuele')

cd /mnt/genzel/Rat/HM/Rat_HM_Ephys/mda_extracted_postsleep % folder where the downsampled files are stored
% ask the user to select the recording to load
folder = uigetdir("title","Select the folder containing the downsampled .mda files"); 
idcs   = strfind(folder,'/');
dir_end  = folder(idcs(end-1):idcs(end));
trimmed=dir_end(2:end-1);
temp=strfind(trimmed,'.');
trimmed=trimmed(1:temp-1);
name_nt=strcat(trimmed,'.nt');
mkdir('/home/genzel/Desktop/Emanuele/artifact_detector/processed/HM/',trimmed) %  make a folder where to store the processed signal
saved=strcat('/home/genzel/Desktop/Emanuele/artifact_detector/processed/HM/',trimmed);
cd(folder)

temp=split(trimmed,'.');
temp=temp(1);
temp=split(temp,'_');
temp1=cell2mat(temp(4));
rat_number=str2num(temp1(4:end)); 


rat_trodes=[30,14;13,8;0,0;28,8;29,22;0,0;30,24;30,22]; %list of trode number per animal. Change it if better trodes are identified
rat_channels=ones(size(rat_trodes)); %we have used so far always the first channel per tetrode, but that can easily be changed

pfc_o=[rat_trodes(rat_number,1),rat_channels(rat_number,1)];
hpc_o=[rat_trodes(rat_number,2),rat_channels(rat_number,2)];

fs=600; % sampling frequency 
dirFiles = dir(folder);
recs=[];
j=0;

% load the files from the selected folder and store them in the matrix recs
for i=1:length(dirFiles)
     name=dirFiles(i).name;
    try
        temp=readmda(name);
        j=j+1;
        recs(1+(j-1)*4:j *4,:)=temp;
        del1=split(name,'.');
        del2=cell2mat(del1(2));
        num(j)=str2num(del2(3:end)); % store the number of the tetrode currently opened
    catch continue
    end  
end
% convert the number of the selected prefrontal and hippocampal channel into the new location in the matrix
pfct=find(num==pfc_o(1));   
hpct=find(num==hpc_o(1));
pfc=(pfct-1)*4+pfc_o(2); 
hpc=(hpct-1)*4+hpc_o(2);
chan=[pfc,hpc];
recs=recs'; % transpose the matrix
% call a custom function that loads the sleepscoring file and returns the
% selection of the NREM periods
recs = sleepscoring(recs,trimmed); 
clear temp
%% 2 - create additional columns of the recs variable,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                and saves the variable

if rem(size(recs,2),4)==0
    recs(:,size(recs,2)+1)=mean(recs,2); %add an average of all channels
end

%% 3 - Fieldtrip ICA
%
%Set up the data: the structure has to look like so
%          label: {151x1 cell}      the channel labels represented as a cell-array of strings
%           time: {1x266 cell}      the time axis [1*Ntime double] per trial
%          trial: {1x266 cell}      the numeric data as a cell array, with a matrix of [151*Ntime double] per trial
%            cfg: [1x1 struct]      the configuration used by the function that generated this data structure

data.time=create_timecell(size(recs,1)/2,size(recs,2),600);
data.time=data.time(1);
for i=1:size(recs,2)
    data.label{i}=strcat('CH',int2str(i));
end
N=33; %number of trials. 
recs_trimmed=recs(1:end-rem(length(recs),N),:);
for i=1:N
    data.trial{i}=recs_trimmed((i-1)*length(recs_trimmed)/N+1:(i)*length(recs_trimmed)/N,:)';
end

data.time=create_timecell(length(recs_trimmed)/N/2,N,fs);
recs=recs_trimmed;
% Run  ICA
cfg.method='fastica';

[comp]=ft_componentanalysis(cfg,data);


% calculate variance explained by each component
dat = data.trial;    
if iscell(dat)
 C  = zeros(size(dat{1},1));
 nC = 0;
 for k = 1:numel(dat)
  C  = C + (dat{k}*dat{k}');
  nC = nC + size(dat{k},2);
 end
 C = C./(nC-1);
else
 C = (dat*dat')./(size(dat,2)-1);
end
[~,D] = eig(C);
d = cat(2,(1:size(recs,2))',diag(D));
d = sortrows(d,[-2]);
varianza=d(1:size(recs,2),2)/sum(diag(C));

for i=1:size(comp.trial,2)
    IC(:,1+size(comp.trial{1},2)*(i-1):size(comp.trial{1},2)*(i))=comp.trial{i};
end

%% 4 - reconstruct the matrices and save the file

if size(recs,2)~=size(IC,2)
    recs=recs';
end
data_gen.name=trimmed;
data_gen.ic=IC;
data_gen.recs=recs;
data_gen.variance=varianza;
data_gen.chan=chan;
data_gen.comp=comp;
save_folder=strcat('/home/genzel/Desktop/Emanuele/processed_data/preproc/',trimmed);
save(save_folder,'data_gen','-v7.3')
