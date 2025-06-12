import React from 'react'

const Card = ({title,value,percentage}) => {
  return (
    <div className='bg-white w-1/4 flex flex-col border rounded-lg  p-4'>
    <div className='text-lg text-gray-500'>{title}</div>
      <div className='flex justify-between items-center mt-2'>
        <div className='text-4xl font-semibold'>{value}</div>
        <div className={`w-14 h-6 flex justify-center items-center ${percentage > 0 ? 'text-black bg-gray-100 rounded-lg p-1 text-sm ' : 'text-white bg-gray-900 rounded-lg p-1 text-sm'}`}>
        <div>{percentage > 0 ? '+' : ''}{percentage}%</div>  
        </div>
      </div>
    </div>
  )
}

export default Card
