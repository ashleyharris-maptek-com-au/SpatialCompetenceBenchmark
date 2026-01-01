// assembly_note.txt (not a printable part)
// To build the full cage, you must print 14 copies of each side band (total 56 prints).
// For band index i = 0..13, place the band at Z = i*50 in assembly.
// Export workflow (OpenSCAD): set segH=50 as is, render, export STL.
// The provided transform matrices in this response give base placement for i=0.
// For i>0, add translation in Z by i*50 to the transform.
//
// Corner threaded rods: 4 rods, one per corner, passing through all corner holes.
// Hole diameter is 6.6 mm (clearance for M6).
