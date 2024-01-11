DROP TABLE IF EXISTS SpecimenSession;
DROP TABLE IF EXISTS SpecimenDescriptionSequence;
DROP TABLE IF EXISTS PrimaryAnatomicStructureSequence;

CREATE TABLE SpecimenSession (
    SpecimenSessionID INTEGER PRIMARY KEY,
    FolderID INTEGER,
    ImageID TEXT,
    ImageFileName TEXT,
    SpecificCharacterSet TEXT,
    ImageType TEXT,
    SOPClassUID TEXT,
    SOPInstanceUID TEXT,
    StudyDate TEXT,
    SeriesDate TEXT,
    StudyTime TEXT,
    SeriesTime TEXT,
    AccessionNumber TEXT,
    Modality TEXT,
    Manufacturer TEXT,
    ReferringPhysicianName TEXT,
    StudyDescription TEXT,
    SeriesDescription TEXT,
    InstitutionalDepartmentName TEXT,
    NameOfPhysiciansReadingStudy TEXT,
    ManufacturerModelName TEXT,
    PatientName TEXT,
    PatientID TEXT,
    PatientBirthDate TEXT,
    PatientSex TEXT,
    ClinicalTrialSponsorName TEXT,
    ClinicalTrialProtocolID TEXT,
    ClinicalTrialSiteName TEXT,
    ClinicalTrialSubjectID TEXT,
    DeviceSerialNumber TEXT,
    SoftwareVersions TEXT,
    ProtocolName TEXT,
    StudyInstanceUID TEXT,
    SeriesInstanceUID TEXT,
    StudyID TEXT,
    SeriesNumber INTEGER,
    InstanceNumber INTEGER,
    PatientOrientation TEXT,
    SamplesPerPixel INTEGER,
    PhotometricInterpretation TEXT,
    Rows INTEGER,
    Columns INTEGER,
    BitsAllocated INTEGER,
    BitsStored INTEGER,
    HighBit INTEGER,
    PixelRepresentation INTEGER,
    LossyImageCompression TEXT,
    ContainerIdentifier TEXT,
    IssuerOfTheContainerIdentifierSequence TEXT,
    ContainerTypeCodeSequence TEXT,
    AcquisitionContextSequence TEXT,
    FOREIGN KEY (FolderID) REFERENCES SpecimenDescriptionSequence(FolderID),
    FOREIGN KEY (SpecimenSessionID) REFERENCES SpecimenDescriptionSequence(SpecimenDescriptionSequenceID)
);

CREATE TABLE SpecimenDescriptionSequence ( 
    SpecimenDescriptionSequenceID INTEGER PRIMARY KEY,
    FolderID INTEGER,
    SpecimenIdentifier TEXT,
    SpecimenUID TEXT,
    IssuerOfTheSpecimenIdentifierSequence TEXT,
    SpecimenShortDescription TEXT,
    SpecimenPreparationSequence TEXT,
    FOREIGN KEY (FolderID) REFERENCES PrimaryAnatomicStructureSequence(FolderID),
    FOREIGN KEY (SpecimenDescriptionSequenceID) REFERENCES PrimaryAnatomicStructureSequence(PrimaryAnatomicStructureSequenceID)
);

CREATE TABLE PrimaryAnatomicStructureSequence (
    PrimaryAnatomicStructureSequenceID INTEGER PRIMARY KEY,
    FolderID INTEGER,
    CodeValue TEXT,
    CodingSchemeDesignator TEXT,
    CodeMeaning TEXT
);