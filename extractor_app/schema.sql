DROP TABLE IF EXISTS SpecimenSession;
DROP TABLE IF EXISTS SpecimenDescriptionSequence;
DROP TABLE IF EXISTS PrimaryAnatomicStructureSequence;

CREATE TABLE SpecimenSession (
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
    SpecimenDescriptionSequenceID INTEGER,  -- Foreign key to link with SpecimenDescriptionSequence
    PRIMARY KEY (SOPInstanceUID),
    FOREIGN KEY (SpecimenDescriptionSequenceID) REFERENCES SpecimenDescriptionSequence(SpecimenDescriptionID)
);

CREATE TABLE SpecimenDescriptionSequence ( 
    SpecimenDescriptionID INTEGER PRIMARY KEY,
    PrimaryAnatomicStructureSequence TEXT,
    SpecimenIdentifier TEXT,
    SpecimenUID TEXT,
    IssuerOfTheSpecimenIdentifierSequence TEXT,
    SpecimenShortDescription TEXT,
    SpecimenPreparationSequence TEXT,
    PrimaryAnatomicStructureSequenceID INTEGER,  -- Foreign key to link with PrimaryAnatomicStructureSequence
    FOREIGN KEY (PrimaryAnatomicStructureSequenceID) REFERENCES PrimaryAnatomicStructureSequence(PrimaryAnatomicStructureID)
);

CREATE TABLE PrimaryAnatomicStructureSequence (
    PrimaryAnatomicStructureID INTEGER PRIMARY KEY,
    CodeValue TEXT,
    CodingSchemeDesignator TEXT,
    CodeMeaning TEXT
);