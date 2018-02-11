export class CacheEntry<T> {

	readonly entry: T;

	private entryDate: Date;

	constructor(entry: T) {
		this.entry = entry;
		this.entryDate = new Date();
	}

	get date(): Date {
		return new Date(this.entryDate);
	}

	isStale(): boolean {
		let temp = new Date(this.entryDate);
		let staleDate = new Date(temp.setMinutes(temp.getMinutes() + 30));

		return this.entryDate > staleDate;
	}

}
