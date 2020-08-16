function data = readMEScTStack(varargin)

%READMESCTSTACK - Returns a nonempty subcuboid from a movie in a .mesc file.
%
%  data = READMESCTSTACK( path, msessionIdx, munitIdx, channelIdx, subcuboid )
%  returns a nonempty subcuboid of a .mesc movie measurement unit.
%
%  INPUTS[required]:
%       path        .mesc file path
%       msessionIdx measurement session index (usually 0)
%       munitIdx    measurement unit index (indexed from 0)
%       channelIdx  channel index (indexed from 0)
%
%  INPUTS[optional]:
%       subcuboid   3D rectangular subcuboid of the data
%                   format: [ymin, xmin, tmin, numy, numx, numt]
%                   where y, x, and t follow the MATLAB convention
%                   SUBCUBOID is optional, if omitted, the whole movie
%                   is returned
%
%  OUTPUT:           
%       data        the frame specified by input parameters
%
%  See also readMEScMovieFrame writeMEScTStack

if nargin < 4
    error('usage: data = readMEScTStack(path, msessionIdx, munitIdx, channelIdx, subcuboid)')
end
path = varargin{1};
msessionIdx = varargin{2};
munitIdx = varargin{3};
channelIdx = varargin{4};

% open HDF5 file for reading
try
    fileID=H5F.open(path, 'H5F_ACC_RDONLY', 'H5P_DEFAULT');
catch
    error('Unable to open file "%s".', path)
end

% open the HDF5 group representing the measurement unit
groupname=sprintf('/MSession_%d/MUnit_%d', msessionIdx, munitIdx);
try
    groupID=H5G.open(fileID, groupname);
catch me
    error('Unable to open measurement unit.')
end

% open the HDF5 dataset holding the channel contents
try
    datasetID=H5D.open(fileID, ...
    sprintf('%s/Channel_%d', groupname, channelIdx));
catch me
    error('Unable to open channel.')
end

% get the necessary attributes
attribID=H5A.open_name(groupID, 'XDim');
xdim=double(H5A.read(attribID, 'H5ML_DEFAULT'));
H5A.close(attribID);
attribID=H5A.open_name(groupID, 'YDim');
ydim=double(H5A.read(attribID, 'H5ML_DEFAULT'));
H5A.close(attribID);
attribID=H5A.open_name(groupID, 'ZDim');
zdim=double(H5A.read(attribID, 'H5ML_DEFAULT'));
H5A.close(attribID);
% if frameIdx >= zdim
%     error('Section index is too large; section does not exist.')
% end

% NumAllUnits = getMEScAttribs(path, 'VecMUnitsSize', 0);

if nargin >= 5
    subcuboid = double(varargin{5});
    if isinf(subcuboid(6))
        subcuboid(6) = zdim - subcuboid(3) + 1;
    end
    if ~ismatrix(subcuboid)
        error('subcuboid should be [xmin, ymin, tmin, numx, numy, numt]')
    end
    s=size(subcuboid);
    if 1 ~= s(1) || 6 ~= s(2)
        error('subcuboid should be [xmin, ymin, tmin, numx, numy, numt]')
    end
    if any(subcuboid < 1)
         error('all subcuboid elements must be positive')
    end
    if subcuboid(1) + subcuboid(4) > ydim + 1 ...
            || subcuboid(2) + subcuboid(5) > xdim + 1 ...
            || subcuboid(3) + subcuboid(6) > zdim + 1
        error(['subcuboid should fit into the data cuboid [1,1,1,', ...
            num2str(ydim), ',', num2str(xdim), ',', num2str(zdim), ']'])
    end
else
    subcuboid = [1, 1, 1, ydim, xdim, zdim];
end

attribID=H5A.open_name(groupID, ...
    sprintf('Channel_%d_Conversion_ConversionLinearOffset',channelIdx));
offset=double(H5A.read(attribID, 'H5ML_DEFAULT'));
H5A.close(attribID);
attribID=H5A.open_name(groupID, ...
    sprintf('Channel_%d_Conversion_ConversionLinearScale',channelIdx));
minusScale=-double(H5A.read(attribID, 'H5ML_DEFAULT'));
H5A.close(attribID);

start = double([subcuboid(3)-1, ydim-subcuboid(1)-subcuboid(4)+1, ... 
    subcuboid(2)-1]);
stride = [1 1 1];
count = [1 1 1];
block = double([subcuboid(6), subcuboid(4), subcuboid(5)]);
dataspaceID = H5D.get_space(datasetID);
H5S.select_hyperslab(dataspaceID,'H5S_SELECT_SET',start,stride,count,block);
dataspaceID_memory = H5S.create_simple(3,block,[]);

% offset = 65535; % DEBUG
% minusScale = 1; % DEBUG
% 
% data = int16(offset - minusScale * double(rot90( ...
%     H5D.read(datasetID, 'H5ML_DEFAULT', dataspaceID_memory, ...
%     dataspaceID, 'H5P_DEFAULT'))));

data = int16(offset - minusScale *double(rot90( ...
    H5D.read(datasetID, 'H5ML_DEFAULT', dataspaceID_memory, ...
    dataspaceID, 'H5P_DEFAULT'))));


% HDF5 objects and files are closed automatically on function exit

%% some old and obsolete stuff
% % rotate 90 and switch to 0-starting indexing:
% % region = [region(3)-1, region(4)-1, xdim - region(2), xdim - region(1)];
% region = [xdim-region(4), xdim-region(3), ydim-region(2), ydim-region(1)];
% %region = [xdim-region(4), xdim - region(3), ydim-region(4), ydim-region(1)];
