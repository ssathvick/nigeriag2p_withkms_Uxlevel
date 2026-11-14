'use client';

import { useState, useCallback, useEffect } from 'react';
import Cropper, { Area, Point } from 'react-easy-crop';
import { X, Minus, Plus, RotateCw } from 'lucide-react';
import { useTranslations } from 'next-intl';
import getCroppedImg from '@/shared/utils/cropImage';

interface ImageCropperProps {
    image: string;
    onCropComplete: (croppedImage: string) => void;
    onCancel: () => void;
}

export default function ImageCropper({ image, onCropComplete, onCancel }: ImageCropperProps) {
    const t = useTranslations();
    const [crop, setCrop] = useState<Point>({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const [rotation, setRotation] = useState(0);
    const [aspect, setAspect] = useState(1);
    const [inputWidth, setInputWidth] = useState<string>('1');
    const [inputHeight, setInputHeight] = useState<string>('1');
    const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);

    useEffect(() => {
        const w = Number(inputWidth);
        const h = Number(inputHeight);

        if (w > 0 && h > 0) {
            setAspect(w / h);
        }
    }, [inputWidth, inputHeight]);

    const onCropChange = (crop: Point) => {
        setCrop(crop);
    };

    const onZoomChange = (zoom: number) => {
        setZoom(zoom);
    };

    const onCropCompleteCallback = useCallback((_ref: Area, _croppedAreaPixels: Area) => {
        setCroppedAreaPixels(_croppedAreaPixels);
    }, []);

    const handleApply = async () => {
        try {
            if (croppedAreaPixels) {
                const croppedImage = await getCroppedImg(image, croppedAreaPixels, rotation);
                if (croppedImage) {
                    onCropComplete(croppedImage);
                }
            }
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="fixed inset-0 z-100 flex items-center justify-center bg-neutral-first/80 p-4">
            <div className="relative w-full max-w-175 bg-neutral-second rounded-[10px] overflow-hidden border-4 border-primary-first">
                {/* Header */}
                <div className="flex items-center justify-between px-8 py-6">
                    <h2 className="text-primary-second text-2xl font-bold font-roboto">{t('edit_image')}</h2>
                    <button
                        onClick={onCancel}
                        className="text-secondary-third hover:text-neutral-first/70 transition-colors"
                    >
                        <X size={32} />
                    </button>
                </div>

                {/* Cropper Area */}
                <div className="relative mx-8 h-87.5 bg-neutral-first rounded-[10px] overflow-hidden">
                    <Cropper
                        image={image}
                        crop={crop}
                        zoom={zoom}
                        rotation={rotation}
                        aspect={aspect}
                        onCropChange={onCropChange}
                        onZoomChange={onZoomChange}
                        onRotationChange={setRotation}
                        onCropComplete={onCropCompleteCallback}
                    />
                </div>

                {/* Controls */}
                <div className="px-8 py-8 flex items-center gap-6 bg-secondary-first/50 w-full">

                    {/* Zoom  */}
                    <div className="flex items-center gap-3 flex-1">
                        <button
                            onClick={() => setZoom(Math.max(1, zoom - 0.1))}
                            className="text-secondary-third hover:text-neutral-first/70 transition-colors"
                        >
                            <Minus size={20} strokeWidth={3} className="border-2 border-secondary-third rounded-full p-0.5" />
                        </button>

                        <div className="relative flex-1 h-1.5 bg-secondary-second rounded-full overflow-hidden">
                            <input
                                type="range"
                                value={zoom}
                                min={1}
                                max={3}
                                step={0.1}
                                onChange={(e) => setZoom(Number(e.target.value))}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                            />
                            <div
                                className="absolute top-0 left-0 h-full bg-primary-first"
                                style={{ width: `${((zoom - 1) / 2) * 100}%` }}
                            />
                        </div>

                        <button
                            onClick={() => setZoom(Math.min(3, zoom + 0.1))}
                            className="text-secondary-third hover:text-neutral-first/70 transition-colors"
                        >
                            <Plus size={20} strokeWidth={3} className="border-2 border-secondary-third rounded-full p-0.5" />
                        </button>
                    </div>

                    {/* Aspect Ratio*/}
                    <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs text-neutral-first/50 font-semibold">{t('width')}</span>
                        <input
                            type="number"
                            value={inputWidth}
                            onChange={(e) => setInputWidth(e.target.value)}
                            className="w-20 px-2 py-1 text-sm border border-secondary-third rounded outline-none focus:border-gray-500"
                        />

                        <span className="text-secondary-third font-bold">:</span>

                        <span className="text-xs text-neutral-first/50 font-semibold">{t('height')}</span>
                        <input
                            type="number"
                            value={inputHeight}
                            onChange={(e) => setInputHeight(e.target.value)}
                            className="w-20 px-2 py-1 text-sm border border-secondary-third rounded outline-none focus:border-gray-500"
                        />
                    </div>

                    {/* Rotate */}
                    <button
                        onClick={() => setRotation((prev) => (prev + 90) % 360)}
                        className="text-secondary-third hover:text-primary-second transition-colors shrink-0"
                        title="Rotate 90°"
                    >
                        <RotateCw size={22} />
                    </button>

                    {/* Apply */}
                    <button
                        onClick={handleApply}
                        className="bg-neutral-first text-neutral-second px-8 py-2 rounded-[10px] font-bold text-sm hover:bg-secondary-second-800 transition-colors shadow-lg shrink-0"
                    >
                        {t('apply')}
                    </button>

                </div>



            </div>
        </div>
    );
}
