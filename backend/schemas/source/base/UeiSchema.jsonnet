local Base = import '../base/Base.libsonnet';

local Root = Base.Types.object {
  properties: {
    uei: Base.Compound.UniqueEntityIdentifier,
  },
  required: ['uei'],
};

Root
