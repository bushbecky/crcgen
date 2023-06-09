#!/usr/bin/env python3
#
#  Test of CRC generator.
#
#   Copyright (C) 2020-2023 Michael Büsch <m@bues.ch>
#
#  Some CRC implementations are derived from AVR-libc.
#  These copyright notices apply to the AVR-libc parts:
#
#   Copyright (c) 2002, 2003, 2004  Marek Michalkiewicz
#   Copyright (c) 2005, 2007 Joerg Wunsch
#   Copyright (c) 2013 Dave Hylands
#   Copyright (c) 2013 Frederic Nadeau
#   All rights reserved.
#
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#   * Neither the name of the copyright holders nor the names of
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#

from libcrcgen import *
from libcrcgen.generator_test import *
from libcrcgen.reference import *
from libcrcgen.util import *
import multiprocessing
import random


# Derived from CRC-32 version 2.0.0 by Craig Bruce, 2006-04-29. (Public Domain):
def crc32(crc, data):
	crcTable = (
		0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535,
		0x9E6495A3, 0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988, 0x09B64C2B, 0x7EB17CBD,
		0xE7B82D07, 0x90BF1D91, 0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D,
		0x6DDDE4EB, 0xF4D4B551, 0x83D385C7, 0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC,
		0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5, 0x3B6E20C8, 0x4C69105E, 0xD56041E4,
		0xA2677172, 0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B, 0x35B5A8FA, 0x42B2986C,
		0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59, 0x26D930AC,
		0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,
		0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924, 0x2F6F7C87, 0x58684C11, 0xC1611DAB,
		0xB6662D3D, 0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F,
		0x9FBFE4A5, 0xE8B8D433, 0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB,
		0x086D3D2D, 0x91646C97, 0xE6635C01, 0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E,
		0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457, 0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA,
		0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65, 0x4DB26158, 0x3AB551CE,
		0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB, 0x4369E96A,
		0x346ED9FC, 0xAD678846, 0xDA60B8D0, 0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,
		0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409,
		0xCE61E49F, 0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81,
		0xB7BD5C3B, 0xC0BA6CAD, 0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A, 0xEAD54739,
		0x9DD277AF, 0x04DB2615, 0x73DC1683, 0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8,
		0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1, 0xF00F9344, 0x8708A3D2, 0x1E01F268,
		0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7, 0xFED41B76, 0x89D32BE0,
		0x10DA7A5A, 0x67DD4ACC, 0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5, 0xD6D6A3E8,
		0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
		0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF,
		0x4669BE79, 0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236, 0xCC0C7795, 0xBB0B4703,
		0x220216B9, 0x5505262F, 0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7,
		0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D, 0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A,
		0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713, 0x95BF4A82, 0xE2B87A14, 0x7BB12BAE,
		0x0CB61B38, 0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21, 0x86D3D2D4, 0xF1D4E242,
		0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777, 0x88085AE6,
		0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,
		0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2, 0xA7672661, 0xD06016F7, 0x4969474D,
		0x3E6E77DB, 0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5,
		0x47B2CF7F, 0x30B5FFE9, 0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605,
		0xCDD70693, 0x54DE5729, 0x23D967BF, 0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94,
		0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D,
	)
	return (crc >> 8) ^ crcTable[(crc ^ data) & 0xFF]

# Derived from AVR-libc:
def crc16(crc, data):
	crc ^= data
	for i in range(8):
		if crc & 1:
			crc = (crc >> 1) ^ 0xA001
		else:
			crc = (crc >> 1)
	return crc
 
# Derived from AVR-libc:
def crc16_ccitt(crc, data):
	data ^= crc & 0xFF
	data = (data ^ (data << 4)) & 0xFF
	return ((((data << 8) & 0xFFFF) | (crc >> 8)) ^
		(data >> 4) ^
		((data << 3) & 0xFFFF))

def crc16_ccitt_reversed(crc, data):
	return bitreverse(crc16_ccitt(bitreverse(crc, 16),
				      bitreverse(data, 8)),
			  16)

# Derived from AVR-libc:
def crc16_xmodem(crc, data):
	crc ^= (data << 8)
	for i in range(8):
		if crc & 0x8000:
			crc = ((crc << 1) ^ 0x1021) & 0xFFFF
		else:
			crc = (crc << 1) & 0xFFFF
	return crc

# Derived from AVR-libc:
def crc8_ibutton(crc, data):
	crc ^= data
	for i in range(8):
		if crc & 1:
			crc = (crc >> 1) ^ 0x8C
		else:
			crc = (crc >> 1)
	return crc

# Derived from AVR-libc:
def crc8_ccitt(crc, data):
	crc ^= data
	for i in range(8):
		if crc & 0x80:
			crc = ((crc << 1) ^ 0x07) & 0xFF
		else:
			crc = (crc << 1) & 0xFF
	return crc

def crc6_itu(crc, data):
	for i in range(8):
		crc ^= (data & 0x80) >> 2
		data <<= 1
		if crc & 0x20:
			crc = ((crc << 1) ^ 0x03) & 0x3F
		else:
			crc = (crc << 1) & 0x3F
	return crc

def crcRange(nrBits):
	rng = random.Random()
	rng.seed(42)
	mask = (1 << nrBits) - 1
	for i in range(0x300):
		if i == 0:
			crc = 0
		elif i == 1:
			crc = mask
		else:
			crc = rng.randint(1, mask - 1)
		yield crc

def dataRange():
	yield from (0x00, 0xAA, 0x55, 0xFF,
		    0x3E, 0x92, 0x0A, 0x7D, 0x4E, 0x07, 0x23, 0xDD,
		    0x4C, 0xE4, 0x1E, 0x8B, 0x5C, 0xD8, 0x1F, 0x74)

def compareReferenceImpl(name, crcFunc):
	print("Testing %s..." % name)
	crcParameters = CRC_PARAMETERS[name]
	for crc in crcRange(crcParameters["nrBits"]):
		for data in dataRange():
			for i in range(5): # Run a couple of iterations.
				a = crcFunc(crc, data)
				b = CrcReference.crc(crc=crc,
						     data=data,
						     polynomial=crcParameters["polynomial"],
						     nrCrcBits=crcParameters["nrBits"],
						     shiftRight=crcParameters["shiftRight"])
				if a != b:
					raise Exception("%s test FAILED!" % name)
				crc = a
				data = (data + 1) & 0xFF

def checkReferenceReversed(nrCrcBits, polynomial):
	print(f"Testing CrcReference reversed ({nrCrcBits=}, P={polynomial:X})...")
	for shiftRight in (True, False):
		for crc in crcRange(nrCrcBits):
			for data in dataRange():
				a = CrcReference.crc(
						crc=crc,
						data=data,
						polynomial=polynomial,
						nrCrcBits=nrCrcBits,
						shiftRight=shiftRight)
				b = bitreverse(CrcReference.crc(
						crc=bitreverse(crc, nrCrcBits),
						data=bitreverse(data, 8),
						polynomial=bitreverse(polynomial, nrCrcBits),
						nrCrcBits=nrCrcBits,
						shiftRight=not shiftRight),
					nrCrcBits)
			if a != b:
				raise Exception("CrcReference reversed test "
						"FAILED! (nrCrcBits=%d, P=%X)" % (
						nrCrcBits, polynomial))

def checkReferenceNrDataBits(nrCrcBits, polynomial):
	print(f"Testing CrcReference with different data word length "
	      f"({nrCrcBits=}, P={polynomial:X})...")
	data = bytes(dataRange())
	for littleEndian in (False, True):
		refCrc = CrcReference.crcBlock(crc=0,
					       data=data,
					       polynomial=polynomial,
					       nrCrcBits=nrCrcBits,
					       nrDataBits=8,
					       shiftRight=littleEndian)

		crc_data16 = 0
		for i in range(0, len(data), 2):
			if littleEndian:
				word = data[i] | (data[i + 1] << 8)
			else:
				word = data[i + 1] | (data[i] << 8)
			crc_data16 = CrcReference.crc(
					crc=crc_data16,
					data=word,
					polynomial=polynomial,
					nrCrcBits=nrCrcBits,
					nrDataBits=16,
					shiftRight=littleEndian)
		if refCrc != crc_data16:
			raise Exception(f"CrcRefernce 16 bit word test FAILED! "
					f"({nrCrcBits=}, P={polynomial:X})")

		crc_data32 = 0
		for i in range(0, len(data), 4):
			if littleEndian:
				word = (data[i] | (data[i + 1] << 8) |
					(data[i + 2] << 16) | (data[i + 3] << 24))
			else:
				word = (data[i + 3] | (data[i + 2] << 8) |
					(data[i + 1] << 16) | (data[i] << 24))
			crc_data32 = CrcReference.crc(
					crc=crc_data32,
					data=word,
					polynomial=polynomial,
					nrCrcBits=nrCrcBits,
					nrDataBits=32,
					shiftRight=littleEndian)
		if refCrc != crc_data32:
			raise Exception(f"CrcRefernce 32 bit word test FAILED! "
					f"({nrCrcBits=}, P={polynomial:X})")

def compareGeneratedImpl(optimize, alg, crcParameters, quick):
	if quick == "quick":
		dataBitsRange = (8, 16)
	else:
		dataBitsRange = (8, 16, 24, 32, 33, 1)
	for nrDataBits in dataBitsRange:
		gen = CrcGenTest(P=crcParameters["polynomial"],
				 nrCrcBits=crcParameters["nrBits"],
				 nrDataBits=nrDataBits,
				 shiftRight=crcParameters["shiftRight"],
				 optimize=optimize)
		gen.runTests(name=alg, extra=("-O=%d" % optimize))

if __name__ == "__main__":
	assert bitreverse(0xE0, 8) == 0x07
	assert bitreverse(0x8408, 16) == 0x1021
	assert bitreverse(0xEDB88320, 32) == 0x04C11DB7

	print("*** Testing polynomial coefficient conversion ***")
	for poly, polyString, nrBits, shiftRight in (
			(0xC96C5795D7870F42,
			 "x^64 + x^62 + x^57 + x^55 + x^54 + x^53 + x^52 + x^47 + "
			 "x^46 + x^45 + x^40 + x^39 + x^38 + x^37 + x^35 + x^33 + "
			 "x^32 + x^31 + x^29 + x^27 + x^24 + x^23 + x^22 + x^21 + "
			 "x^19 + x^17 + x^13 + x^12 + x^10 + x^9 + x^7 + x^4 + x + 1",
			 64, True),
			(0xEDB88320,
			 "x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + "
			 "x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1",
			 32, True),
			(0xa001,
			 "x^16 + x^15 + x^2 + 1",
			 16, True),
			(0x1021,
			 "x^16 + x^12 + x^5 + 1",
			 16, False),
			(0x8408,
			 "x^16 + x^12 + x^5 + 1",
			 16, True),
			(0x8C,
			 "x^8 + x^5 + x^4 + 1",
			 8, True),
			(0xE0,
			 "x^8 + x^2 + x + 1",
			 8, True),
			(0x07,
			 "x^8 + x^2 + x + 1",
			 8, False),
			(0x03,
			 "x^3 + x + 1",
			 3, False),
			(0x01,
			 "x^3 + 1",
			 3, False),
			(0x02,
			 "x^3 + x",
			 3, False),
		):
		print("Testing %s..." % polyString)
		if poly2int(polyString, nrBits, shiftRight) != poly:
			raise Exception("Polynomial '%s' != 0x%X" % (polyString, poly))
		if int2poly(poly, nrBits, shiftRight) != polyString:
			raise Exception("Polynomial 0x%X != '%s'" % (poly, polyString))

	print("*** Comparing reference implementation to itself reversed ***")
	params = (
		(32, 0xEDB88320),
		(16, 0xA001),
		(16, 0x1021),
		(8, 0x07),
		(8, 0x8C),
	)
	with multiprocessing.Pool() as p:
		p.starmap(checkReferenceReversed, params)

	print("*** Comparing reference implementation to itself with different data word length ***")
	params = (
		(32, 0xEDB88320),
		(16, 0xA001),
		(16, 0x1021),
		(8, 0x07),
		(8, 0x8C),
	)
	with multiprocessing.Pool() as p:
		p.starmap(checkReferenceNrDataBits, params)

	print("*** Comparing reference implementation to discrete implementations ***")
	params = (
		("CRC-32", crc32),
		("CRC-16", crc16),
		("CRC-16-CCITT", crc16_ccitt_reversed),
		("CRC-16-CCITT", crc16_xmodem),
		("CRC-8-CCITT", crc8_ccitt),
		("CRC-8-IBUTTON", crc8_ibutton),
		("CRC-6-ITU", crc6_itu),
	)
	with multiprocessing.Pool() as p:
		p.starmap(compareReferenceImpl, params)

	def makeParams(allOptPermut, quick="not_quick"):
		if allOptPermut:
			for optimize in reversed(range(1 << CrcGen.OPT_ALL.bit_length())):
				yield optimize, "CRC-16", CRC_PARAMETERS["CRC-16"], quick
		else:
			for alg, crcParameters in CRC_PARAMETERS.items():
				yield CrcGen.OPT_ALL, alg, crcParameters, quick
	print("*** Comparing generated CRC functions "
	      "to reference implementation (with all optimization option permutations)***")
	with multiprocessing.Pool() as p:
		p.starmap(compareGeneratedImpl, tuple(makeParams(allOptPermut=True, quick="quick")))
	print("*** Comparing all generated CRC functions "
	      "to reference implementation (with full optimization)***")
	with multiprocessing.Pool() as p:
		p.starmap(compareGeneratedImpl, tuple(makeParams(allOptPermut=False)))
