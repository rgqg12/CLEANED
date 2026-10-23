import pickle, sys, types
ALLOWED=('pandas','numpy','builtins','copyreg','collections','datetime')
class Stub:  # stands in for salcabd.ControlTable / Validator
    def __init__(self,*a,**k): pass
    def __setstate__(self,s): self.__dict__.update(s if isinstance(s,dict) else {'state':s})
class R(pickle.Unpickler):
    def find_class(self,mod,name):
        if mod.startswith('salcabd'): return Stub
        if mod=='pandas.core.indexes.numeric':
            import pandas as pd; return pd.Index
        if mod.split('.')[0] in ALLOWED:
            if mod=='builtins' and name not in ('slice','complex','set','frozenset','object','getattr'): raise pickle.UnpicklingError(name)
            return super().find_class(mod,name)
        raise pickle.UnpicklingError(f'blocked {mod}.{name}')
ct=R(open(sys.argv[1],'rb')).load()
import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_rows',200)
print(ct.__dict__.keys())
print(ct.indicator_df)
cdf=ct.control_df; print(cdf.shape); print(cdf.index.names)
print(cdf.index.get_level_values('Habitat Type I').value_counts())
ct.control_df.to_pickle(sys.argv[2]+'/control_df.pkl'); ct.indicator_df.to_csv(sys.argv[2]+'/indicator.csv'); ct.minmax_df.to_csv(sys.argv[2]+'/minmax.csv')
