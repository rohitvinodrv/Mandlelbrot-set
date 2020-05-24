from numba import njit
import numpy
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from matplotlib import pyplot as plt 
from PIL import Image
# import os
from time import perf_counter

@njit(nogil=True)
def n_generate(result, itr, oprange_re, oprange_img):
	r_val = result[0,0]

	result = result[1:,:]
	
	def scale(val, inp_range, op_range):
		return val*(op_range[1]-op_range[0])/(inp_range[1]-inp_range[0]) + op_range[0]    
    

	def mb_set(re,im, max_iter):
	    c = complex(re,im)
	    z = 0.0j
	    for i in range(max_iter):
	        z = z*z + c
	        if (z.real*z.real + z.imag*z.imag) >= 4:
	            return i

	    return max_iter
   
	r_val1, r_val2  = scale(r_val,(0,8),oprange_re), scale(r_val+1,(0,8), oprange_re)
	rows, columns = result.shape
	# increment_val = (oprange_re[1]-oprange_re[0])/4	# the 4 used here is the cpu count /2
	for i in range(rows):
	#         print(i)
	    re = scale(i,(0,rows),(r_val1,r_val2))
	    for j in range(columns):
	        img = scale(j,(0,columns),oprange_img)
	        result[i,j] = mb_set(re,img,itr)

	return result


def parallel_generate(rs, cs, miter, oprange_re, oprange_img):
	rs_8 = int(rs/8)
	t1 = perf_counter()
	mat = numpy.zeros([rs_8,cs])
	# print("mat shape=",mat.shape)
	new_mat = numpy.full([1,rs_8+1,cs],0)
	for i in range(8):
		temp = numpy.array([numpy.full(cs,i)])
		temp = numpy.array([numpy.append(temp,mat,0)])
		new_mat = numpy.append(new_mat,temp,0)

	# t1 = perf_counter()

	mat = numpy.zeros([1,cs])
	new_mat = numpy.delete(new_mat,0,0)
	# print("entered with")
	# print(new_mat.shape)
	# t2 = perf_counter()
	with ProcessPoolExecutor() as pool:
		results = pool.map(partial(n_generate,itr=miter, oprange_re=oprange_re, oprange_img=oprange_img),new_mat)
		for result in results:
			# print("in for loop")
			mat = numpy.append(mat,result,0)
			# print(result)

	return mat[1:,:]



if __name__ == '__main__':

	mat = parallel_generate(1920,1080,500, (-0.6890668523676879, -0.43906685236768794), (-0.7709424083769634, -0.5209424083769634)).T
	cmap = plt.cm.hot
	norm = plt.Normalize(vmin=mat.min(),vmax=mat.max())
	image = cmap(norm(mat))
	im = Image.fromarray(numpy.uint8(image*255))
	im.show()
