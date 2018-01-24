from pypismplot import PISMDataset

import matplotlib.pyplot as plt

#test_data = PISMDataset('test/test_data.nc', 'r')

plt.close('all')
plt.figure(1)

#test_data.pcolormesh('velbase_mag', t=5000, mask_var='thk', mask_thold=100, cmap='jet')
#test_data.pcolormesh('thk', t=5000, mask_var='thk', mask_thold=0.5)
#test_data.pcolormesh('topg', t=5000)

with PISMDataset('test/test_data.nc', 'r') as test_data:
    test_data.pcolormesh('topg', t=5000)

plt.savefig('test.jpg')
plt.close('all')

#test_data.close()
